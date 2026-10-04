# from utils.face_utils.face_service import FaceService

# service = FaceService()

# result = service.register_face(image_path="test.jpg", user_id="123456")

# print(result)
from utils.face_utils.face_service import FaceService

face_service = FaceService()

result = face_service.authenticate_face(
    image_path="meiraba5.png"
)

print(result)