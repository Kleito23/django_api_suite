from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import uuid

# Simulacion de base de datos local en memoria
data_list = []

# Anadiendo algunos datos de ejemplo para probar el GET
data_list.append({'id': str(uuid.uuid4()), 'name': 'User01', 'email': 'user01@example.com', 'is_active': True})
data_list.append({'id': str(uuid.uuid4()), 'name': 'User02', 'email': 'user02@example.com', 'is_active': True})
data_list.append({'id': str(uuid.uuid4()), 'name': 'User03', 'email': 'user03@example.com', 'is_active': False}) # Ejemplo de item inactivo

class DemoRestApi(APIView):
    name = "Demo REST API"

    def get(self, request):
        # Filtra la lista para incluir solo los elementos donde 'is_active' es True
        active_items = [item for item in data_list if item.get('is_active', False)]
        return Response(active_items, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data

        # Validación mínima
        if 'name' not in data or 'email' not in data:
            return Response({'error': 'Faltan campos requeridos.'}, status=status.HTTP_400_BAD_REQUEST)

        data['id'] = str(uuid.uuid4())
        data['is_active'] = True
        data_list.append(data)

        return Response({'message': 'Dato guardado exitosamente.', 'data': data}, status=status.HTTP_201_CREATED)


class DemoRestApiItem(APIView):
    def _find_item(self, item_id):
        for item in data_list:
            if item.get('id') == item_id and item.get('is_active', True):
                return item
        return None

    def put(self, request, item_id):
        data = request.data

        if data.get('id') != item_id:
            return Response(
                {'message': 'El id del cuerpo debe existir y coincidir con el id de la URL.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if 'name' not in data or 'email' not in data:
            return Response(
                {'message': 'Para PUT se requieren los campos id, name y email.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item = self._find_item(item_id)
        if not item:
            return Response(
                {'message': 'Elemento no encontrado o inactivo.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        item.clear()
        item.update(
            {
                'id': item_id,
                'name': data['name'],
                'email': data['email'],
                'is_active': data.get('is_active', True),
            }
        )

        return Response(
            {'message': 'Elemento reemplazado correctamente.', 'data': item},
            status=status.HTTP_200_OK,
        )

    def patch(self, request, item_id):
        data = request.data

        if 'id' in data and data['id'] != item_id:
            return Response(
                {'message': 'El id del cuerpo debe coincidir con el id de la URL.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item = self._find_item(item_id)
        if not item:
            return Response(
                {'message': 'Elemento no encontrado o inactivo.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        updatable_fields = {'name', 'email', 'is_active'}
        updates = {key: value for key, value in data.items() if key in updatable_fields}
        if not updates:
            return Response(
                {'message': 'No se enviaron campos validos para actualizar.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item.update(updates)

        return Response(
            {'message': 'Elemento actualizado parcialmente.', 'data': item},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, item_id):
        item = self._find_item(item_id)
        if not item:
            return Response(
                {'message': 'Elemento no encontrado o ya inactivo.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        item['is_active'] = False
        return Response(
            {'message': 'Elemento eliminado logicamente.', 'data': item},
            status=status.HTTP_200_OK,
        )
