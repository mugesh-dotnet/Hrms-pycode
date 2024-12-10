import os
import pathlib
import face_recognition
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load known faces when the app starts
known_faces = []
known_names = []
known_ids = []


@app.route('/verify', methods=['POST'])
def verify():
    try:
        # Check if the image part exists in the request
        if 'image' not in request.files:
            return jsonify({"status": "failure", "message": "No image part in the request"}), 400
        if 'project_id' not in request.form:
            return jsonify({"status": "failure", "message": "Missing project_id in the request"}), 400
        uploaded_file = request.files['image']

        # Check if a file was selected
        if uploaded_file.filename == '':
            return jsonify({"status": "failure", "message": "No selected file"}), 400

        # Log the filename for debugging purposes
        logging.debug(f"Received file: {uploaded_file.filename}")

        # Load the uploaded image file
        uploaded_image = face_recognition.load_image_file(uploaded_file)

        # Get the face encodings from the uploaded image
        unknown_encodings = face_recognition.face_encodings(uploaded_image)
        # # Iterate over each project directory in the known faces directory
        # for project_id in os.listdir("img check/known_faces"):
        #     project_dir = os.path.join("img check/known_faces", project_id)  # Construct the path for the project
        #
        #     # Ensure the directory exists and is indeed a directory
        #     if os.path.isdir(project_dir):
        #         # Iterate over each name directory in the project directory
        #         for name in os.listdir(project_dir):
        #             name_dir = os.path.join(project_dir, name)  # Construct the path for the name
        #             print(name_dir)
        #             # Ensure the directory exists and is indeed a directory
        #             if os.path.isdir(name_dir):
        #                 # Iterate over all .jpg files in this name's directory
        #                 for file in pathlib.Path(name_dir).glob("*.jpg"):
        #                     logging.debug(f"Loading known face from file: {file}")
        #
        #                     try:
        #                         # Load the image file
        #                         image = face_recognition.load_image_file(str(file))
        #
        #                         # Get the face encodings for the image
        #                         encodings = face_recognition.face_encodings(image)
        #
        #                         # Check if any face encodings were found
        #                         if encodings:
        #                             known_names.append(name)  # Use the name folder as the identifier
        #                             known_faces.append(encodings[0])  # Append the first encoding found
        #                             logging.info(f"Loaded face for {name} with encoding.")
        #                         else:
        #                             logging.warning(f"No face found in image {file}")
        #
        #                     except Exception as e:
        #                         logging.error(f"Error processing file {file}: {e}")
        #             else:
        #                 logging.warning(f"Expected directory not found: {name_dir}")
        #     else:
        #         logging.warning(f"Expected project directory not found: {project_dir}") //2

        # for file in pathlib.Path("img check/known_faces").glob("**/*.jpg"):
        #     logging.debug(f"Loading known face from file: {file}")
        #
        #     # Extract the name using os.path for cross-platform compatibility
        #     name = os.path.basename(os.path.dirname(str(file)))  # Extract 'Ajith Kumar' from the path
        #     image = face_recognition.load_image_file(str(file))
        #
        #     # Get the face encodings for the image
        #     encodings = face_recognition.face_encodings(image)
        #
        #     # Check if any face encodings were found
        #     if encodings:
        #         known_names.append(name)
        #         known_faces.append(encodings[0])  # Only append if face encoding is found
        #     else:
        #         logging.warning(f"No face found in image {file}")//1
        for project_id in os.listdir("/img check/known_faces"):
            project_dir = os.path.join("/img check/known_faces", project_id)  # Construct the path for the project

            # Ensure the directory exists and is indeed a directory
            if os.path.isdir(project_dir):
                # Iterate over each empid directory in the project directory
                for emp_id in os.listdir(project_dir):
                    emp_dir = os.path.join(project_dir, emp_id)  # Construct the path for the empid
                    print(emp_dir)
                    # Ensure the directory exists and is indeed a directory
                    if os.path.isdir(emp_dir):
                        # Iterate over all name directories in the empid's directory
                        for name in os.listdir(emp_dir):
                            name_dir = os.path.join(emp_dir, name)  # Construct the path for the name
                            # Ensure the directory exists and is indeed a directory
                            if os.path.isdir(name_dir):
                                # Iterate over all .jpg files in this name's directory
                                for file in pathlib.Path(name_dir).glob("*.jpg"):
                                    logging.debug(f"Loading known face from file: {file}")

                                    try:
                                        # Load the image file
                                        image = face_recognition.load_image_file(str(file))

                                        # Get the face encodings for the image
                                        encodings = face_recognition.face_encodings(image)

                                        # Check if any face encodings were found
                                        if encodings:
                                            known_names.append(name)  # Use the name folder as the identifier
                                            known_faces.append(encodings[0])  # Append the first encoding found
                                            known_ids.append(emp_id)  # Append the EmpId
                                            logging.info(f"Loaded face for {name} (Emp ID: {emp_id}) with encoding.")
                                        else:
                                            logging.warning(f"No face found in image {file}")

                                    except Exception as e:
                                        logging.error(f"Error processing file {file}: {e}")
                            else:
                                logging.warning(f"Expected directory not found: {name_dir}")
                    else:
                        logging.warning(f"Expected empid directory not found: {emp_dir}")
            else:
                logging.warning(f"Expected project directory not found: {project_dir}")
        if len(known_faces) == 0:
            logging.info("No known faces loaded, returning 'No match found'")
            return jsonify({
                "status": "success",
                "message": "No match found"
            }), 200
        # Check if a face encoding was found in the uploaded image
        if not unknown_encodings:
            return jsonify({"status": "failure", "message": "No face found in the uploaded image"}), 400

        unknown_encoding = unknown_encodings[0]
        logging.debug(f"Unknown face encoding: {unknown_encoding}")

        # Compare the unknown face to the known faces using a strict tolerance
        results = face_recognition.compare_faces(known_faces, unknown_encoding, tolerance=0.4)
        logging.debug(f"Comparison results: {results}")
        print(results)
        # Use face_distance to get a better understanding of how similar the faces are
        face_distances = face_recognition.face_distance(known_faces, unknown_encoding)
        logging.debug(f"Face distances: {face_distances}")
        print(face_distances)
        # Get the best match by checking the smallest distance
        best_match_index = face_distances.argmin()  # Get index of the closest match
        print(best_match_index)
        best_match_distance = face_distances[best_match_index]
        print(best_match_distance)
        logging.debug(f"Best match distance: {best_match_distance}")

        # Check if the best match is within a reasonable threshold
        if best_match_distance < 0.4:  # You can tweak this threshold
            best_match_name = known_names[best_match_index]
            best_match_id = known_ids[best_match_index]
            logging.debug(f"Best match found: {best_match_name}")
            return jsonify({
                "status": "success",
                "message": "Match found",
                "Name": best_match_name,
                "EmpID": best_match_id
            }), 200
        else:
            # No good match found
            logging.info("No close match found")
            return jsonify({
                "status": "success",
                "message": "No match found"
            }), 200

    except Exception as e:
        logging.error(f"Error during face verification: {str(e)}")
        return jsonify({"status": "failure", "message": "An error occurred during verification"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)