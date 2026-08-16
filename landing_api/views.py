import datetime

from firebase_admin import db
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class LandingAPI(APIView):
	name = "Landing API"
	collection_name = "landing_api"

	def _reference(self):
		return db.reference(self.collection_name)

	def _now(self):
		return datetime.datetime.utcnow().isoformat() + "Z"

	def _serialize_collection(self, payload):
		if not payload:
			return []

		if isinstance(payload, dict):
			return [
				{"id": item_id, **item_data}
				for item_id, item_data in payload.items()
				if isinstance(item_data, dict)
			]

		return payload

	def get(self, request):
		collection_ref = self._reference()
		data = collection_ref.get() or {}
		payload = self._serialize_collection(data)
		return Response(payload, status=status.HTTP_200_OK)

	def post(self, request):
		data = request.data.copy()
		now = datetime.datetime.now()
		formatted_timestamp = now.strftime("%d/%m/%Y, %I:%M:%S %p")
		formatted_timestamp = formatted_timestamp.lower()
		formatted_timestamp = formatted_timestamp.replace("am", "a. m.").replace("pm", "p. m.")

		item_ref = self._reference().push()
		payload = {
			**data,
			"timestamp": formatted_timestamp,
		}

		item_ref.set(payload)
		return Response({"id": item_ref.key, "timestamp": formatted_timestamp}, status=status.HTTP_201_CREATED)

	def put(self, request):
		data = request.data.copy()
		item_id = data.get("id")

		if not item_id:
			return Response(
				{"message": "Se requiere el campo id para actualizar el registro."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		item_ref = self._reference().child(item_id)
		existing_item = item_ref.get()

		if not existing_item:
			return Response(
				{"message": "Registro no encontrado."},
				status=status.HTTP_404_NOT_FOUND,
			)

		now = self._now()
		payload = {
			**data,
			"id": item_id,
			"created_at": existing_item.get("created_at", now),
			"updated_at": now,
		}

		item_ref.set(payload)
		return Response(payload, status=status.HTTP_200_OK)

	def patch(self, request):
		data = request.data.copy()
		item_id = data.get("id")

		if not item_id:
			return Response(
				{"message": "Se requiere el campo id para actualizar el registro."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		item_ref = self._reference().child(item_id)
		existing_item = item_ref.get()

		if not existing_item:
			return Response(
				{"message": "Registro no encontrado."},
				status=status.HTTP_404_NOT_FOUND,
			)

		now = self._now()
		payload = {
			**existing_item,
			**data,
			"id": item_id,
			"updated_at": now,
		}

		item_ref.update(payload)
		return Response(payload, status=status.HTTP_200_OK)

	def delete(self, request):
		data = request.data.copy()
		item_id = data.get("id")

		if not item_id:
			return Response(
				{"message": "Se requiere el campo id para eliminar el registro."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		item_ref = self._reference().child(item_id)
		existing_item = item_ref.get()

		if not existing_item:
			return Response(
				{"message": "Registro no encontrado."},
				status=status.HTTP_404_NOT_FOUND,
			)

		item_ref.delete()
		return Response(
			{"message": "Registro eliminado correctamente.", "id": item_id},
			status=status.HTTP_200_OK,
		)
