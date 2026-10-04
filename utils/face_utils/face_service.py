import os
import pickle
import cv2
import numpy as np
from insightface.app import FaceAnalysis


class FaceService:

    def __init__(self):

        self.app = FaceAnalysis()
        self.app.prepare(ctx_id=0)

    def register_face(
        self,
        image_path,
        user_id,
        images_dir="face_data/images",
        embeddings_dir="face_data/embeddings",
    ):

        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(embeddings_dir, exist_ok=True)

        image = cv2.imread(image_path)

        if image is None:
            raise ValueError("Unable to read image")

        faces = self.app.get(image)

        if len(faces) == 0:
            raise ValueError("No face detected")

        if len(faces) > 1:
            raise ValueError("Multiple faces detected")

        face = faces[0]

        saved_image_path = os.path.join(images_dir, f"{user_id}.jpg")

        saved_embedding_path = os.path.join(embeddings_dir, f"{user_id}.pkl")

        cv2.imwrite(saved_image_path, image)

        with open(saved_embedding_path, "wb") as f:
            pickle.dump(face.embedding, f)

        return {"image_path": saved_image_path, "embedding_path": saved_embedding_path}
    
    def register_multiple_faces(
        self,
        image_paths,
        user_id,
        images_dir="face_data/images",
        embeddings_dir="face_data/embeddings"
    ):

        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(embeddings_dir, exist_ok=True)

        first_image_path = None

        for index, image_path in enumerate(image_paths, start=1):

            image = cv2.imread(image_path)

            if image is None:
                continue

            faces = self.app.get(image)

            if len(faces) != 1:
                continue

            face = faces[0]

            saved_embedding_path = os.path.join(
                embeddings_dir,
                f"{user_id}_{index}.pkl"
            )

            with open(saved_embedding_path, "wb") as f:
                pickle.dump(face.embedding, f)

            if first_image_path is None:

                first_image_path = os.path.join(
                    images_dir,
                    f"{user_id}.jpg"
                )

                cv2.imwrite(
                    first_image_path,
                    image
                )

        if first_image_path is None:
            raise ValueError(
                "No valid face images found"
            )

        return {
            "image_path": first_image_path
        }
        
    def cosine_similarity(self, emb1, emb2):

        emb1 = np.array(emb1)
        emb2 = np.array(emb2)

        return np.dot(
            emb1,
            emb2
        ) / (
            np.linalg.norm(emb1)
            * np.linalg.norm(emb2)
        )


    def authenticate_face(
        self,
        image_path,
        embeddings_dir="face_data/embeddings",
        threshold=0.57
    ):

        image = cv2.imread(image_path)

        if image is None:
            raise ValueError("Unable to read image")

        faces = self.app.get(image)

        if len(faces) == 0:
            raise ValueError("No face detected")

        if len(faces) > 1:
            raise ValueError("Multiple faces detected")

        probe_embedding = faces[0].embedding

        best_score = -1
        best_user_id = None

        for filename in os.listdir(embeddings_dir):

            if not filename.endswith(".pkl"):
                continue

            user_id = filename.replace(".pkl", "")

            if "_" in user_id:
                user_id = user_id.split("_")[0]

            file_path = os.path.join(
                embeddings_dir,
                filename
            )

            with open(file_path, "rb") as f:
                stored_embedding = pickle.load(f)

            score = self.cosine_similarity(
                probe_embedding,
                stored_embedding
            )

            if score > best_score:

                best_score = score
                best_user_id = user_id

        if best_score >= threshold:
            print(f"Best Match: {best_user_id} | Score: {best_score}")
            return {
                "authenticated": True,
                "user_id": best_user_id,
                "score": float(best_score)
            }

        return {
            "authenticated": False,
            "score": float(best_score)
        }
