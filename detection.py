import datetime
import io
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from torch.utils.data import DataLoader
from torchvision import datasets
import os
from PIL import Image, ImageDraw
import cv2
import time
from torch.nn import CosineSimilarity
import argparse
import pyttsx3

# def text_to_speech(text):
#     # Initialize the text-to-speech engine
#     engine = pyttsx3.init()

#     # Set properties (optional)
#     engine.setProperty('rate', 150)  # Speed of speech

#     voices = engine.getProperty('voices')

#     # Set the voice to a female voice (you can change the index to select a different voice)
#     engine.setProperty('voice', voices[1].id)  # Assuming the female voice is at index 1


#     # Convert the text to speech
#     engine.say(text)

#     # Wait for the speech to finish
#     engine.runAndWait()



# parser = argparse.ArgumentParser(description="Recognize faces in real time")
# parser.add_argument("--train_in_batches", action="store_true", help="Train on input data in batches")
# parser.add_argument(
#     "--train_only_unknowns", action="store_true", help="Train on unknown photos only"
# )
# parser.add_argument(
#     "--recognize", action="store_true", help="Test the model real time"
# )

# args = parser.parse_args()


workers = 0 if os.name == 'nt' else 4

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print('Running on device: {}'.format(device))



mtcnn0 = MTCNN(image_size=240, margin=0, keep_all=False, min_face_size=40) # keep_all=False
mtcnn = MTCNN(image_size=240, margin=0, keep_all=True, min_face_size=40) # keep_all=True
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

def collate_fn(x):
    return x[0]



def train_unknowns(unknown_images_folder_path,encodings_path):
    existing_encodings = torch.load(encodings_path)
    existing_embedding_list = existing_encodings[0]
    existing_names_list = existing_encodings[1]
    print("existing encodings ", existing_embedding_list)
    print("existing names ", existing_names_list)
    dataset = datasets.ImageFolder(unknown_images_folder_path)
    dataset.idx_to_class = {i:c for c, i in dataset.class_to_idx.items()}
    loader = DataLoader(dataset, collate_fn=collate_fn, num_workers=0)
    name_list = [] # list of names corrospoing to cropped photos
    embedding_list = [] # list of embeding matrix after conversion from cropped faces to embedding matrix using resnet
    for img, idx in loader:
        face, prob = mtcnn0(img, return_prob=True)
        print("face is " ,face)
        if face is not None and prob>0.90:
            emb = resnet(face.unsqueeze(0)) # passing cropped face into resnet model to get embedding matrix
            embedding_list.append(emb.detach()) # resulten embedding matrix is stored in a list
            name_list.append(dataset.idx_to_class[idx]) # names are stored in a list

    all_embeddings = existing_embedding_list + embedding_list

    all_names = existing_names_list + name_list

    # Save concatenated data
    new_data = [all_embeddings, all_names]
    torch.save(new_data, 'data.pt')




def train_in_batches(image_folder_path='C:/Users/SahithReddy/Desktop/pytorch-facerecognition/photos'):
    dataset = datasets.ImageFolder(image_folder_path)
    dataset.idx_to_class = {i:c for c, i in dataset.class_to_idx.items()}
    loader = DataLoader(dataset, collate_fn=collate_fn, num_workers=0)
    name_list = [] # list of names corrospoing to cropped photos
    embedding_list = [] # list of embeding matrix after conversion from cropped faces to embedding matrix using resnet
    for img, idx in loader:
        face, prob = mtcnn0(img, return_prob=True)
        if face is not None and prob>0.90:
            emb = resnet(face.unsqueeze(0)) # passing cropped face into resnet model to get embedding matrix
            embedding_list.append(emb.detach()) # resulten embedding matrix is stored in a list
            name_list.append(dataset.idx_to_class[idx]) # names are stored in a list

    data = [embedding_list, name_list]
    torch.save(data, 'data.pt') # saving data.pt file



def face_match(img_path, data_path): # img_path= location of photo, data_path= location of data.pt
   # getting embedding matrix of the given img
   img = Image.open(img_path)
   # img = Image.open('path_to_image.jpg')


   # Detect faces in the image
   boxes, _ = mtcnn.detect(img)


   # If faces are detected, 'boxes' will contain the bounding box coordinates
   if boxes is not None:
       for box in boxes:
           # Draw bounding boxes on the image
           draw = ImageDraw.Draw(img)
           draw.rectangle(box.tolist(), outline='red', width=3)


   # Display or save the image with detected faces
  #  img.show()
   face, prob = mtcnn(img, return_prob=True) # returns cropped face and probability
   emb = resnet(face[0].unsqueeze(0)).detach() # detech is to make required gradient false


   saved_data = torch.load(data_path) # loading data.pt file
   embedding_list = saved_data[0] # getting embedding data
   name_list = saved_data[1] # getting list of names
   dist_list = [] # list of matched distances, minimum distance is used to identify the person
   cos = CosineSimilarity(dim=1)
   cos_sim_list = []


   for idx, emb_db in enumerate(embedding_list):
       dist = torch.dist(emb, emb_db).item()
       dist_list.append(dist)
       cos_sim = cos(emb, emb_db)
       cos_sim = cos_sim[ 0]
       cos_sim_list.append(cos_sim.item())


   min_dist = min(dist_list) # get minumum dist value
   min_dist_idx = dist_list.index(min_dist) # get minumum dist index
   name = name_list[min_dist_idx] # get name corrosponding to minimum dist


  #  print("name from min distance ", name)
  #  print(min_dist)


   # Take max cosine similarity
   max_cos_sim = max(cos_sim_list)


   # Get index of closest match
   max_idx = cos_sim_list.index(max_cos_sim)


   # Retrieve name using max index
   print("name list is -----------------------",name_list)
   name = name_list[max_idx]








  #  print("name from max simaliarity ", name)
  #  print(max_cos_sim)
   if min_dist<0.90 and max_cos_sim > 0.60:


       text = f"Hello {name}! Welcome to Astreya"
      #  text_to_speech(name)
       return name
   else:
       return 'Unknown'


def real_time_face_detection():
    load_data = torch.load('data.pt')
    embedding_list = load_data[0]
    name_list = load_data[1]

    cam = cv2.VideoCapture(0)
    # Get the default screen resolution
    screen_width = 1920  # Adjust this based on your screen resolution
    screen_height = 1080  # Adjust this based on your screen resolution

    # Set the camera frame width and height
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height)

    # ret, frame = cam.read()


    # # Generate a unique filename based on the current timestamp
    # # timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    # filename = f'captured_image.jpg'

    # # Save the image locally
    # image_path = os.path.join("C:/Users/SahithReddy/Desktop/frontend/Face-Recognition-frontend/src/assets/uploads", filename)
    # cv2.imwrite(image_path, frame)

    cos = CosineSimilarity(dim=1)

    start_time = time.time()
    # while time.time() - start_time < 5:


    while True:
        ret, frame = cam.read()
        if not ret:
            print("fail to grab frame, try again")
            break

        img = Image.fromarray(frame)
        img_cropped_list, prob_list = mtcnn(img, return_prob=True)

        if img_cropped_list is not None:
            boxes, _ = mtcnn.detect(img)

            for i, prob in enumerate(prob_list):
                if prob>0.90:
                    emb = resnet(img_cropped_list[i].unsqueeze(0)).detach()

                    dist_list = [] # list of matched distances, minimum distance is used to identify the person
                    cos_sim_list = []

                    for idx, emb_db in enumerate(embedding_list):
                        dist = torch.dist(emb, emb_db).item()
                        dist_list.append(dist)
                        cos_sim = cos(emb, emb_db)
                        cos_sim = cos_sim[ 0]
                        cos_sim_list.append(cos_sim.item())



                    min_dist = min(dist_list) # get minumum dist value
                    min_dist_idx = dist_list.index(min_dist) # get minumum dist index
                    name = name_list[min_dist_idx] # get name corrosponding to minimum dist

                    # print("name from min distance ", name)
                    # print(min_dist)

                    # Take max cosine similarity
                    max_cos_sim = max(cos_sim_list)

                    # Get index of closest match
                    max_idx = cos_sim_list.index(max_cos_sim)

                    # Retrieve name using max index
                    name = name_list[max_idx]



                    # print("name from max simaliarity ", name)
                    # print(max_cos_sim)

                    box = boxes[i]

                    original_frame = frame.copy() # storing copy of frame before drawing on it

                    if min_dist<0.90 and max_cos_sim > 0.60:
                        frame = cv2.putText(frame, name+' '+str(min_dist)+' '+str(max_cos_sim), (int(box[0]),int(box[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),1, cv2.LINE_AA)

                        if time.time() - start_time >5:
                          text = f"Hello {name}! Welcome to Astreya"
                          # text_to_speech(name)
                          print("face recognized ", name)
                          # encodings_path = "C:/Users/SahithReddy/Desktop/pytorch-facerecognition/data.pt"
                          # existing_encodings = torch.load(encodings_path)
                          # existing_embedding_list = existing_encodings[0]
                          # existing_names_list = existing_encodings[1]
                          # print("existing encodings ", existing_embedding_list)
                          # print("existing names ", existing_names_list)
                          return name



                    else:
                        frame = cv2.putText(frame, 'Unknown '+str(min_dist)+' '+str(max_cos_sim), (int(box[0]),int(box[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),1, cv2.LINE_AA)
                        name = 'Unknown'
                        print("The user is unknown ", name)
                        if time.time() - start_time >5:
                          return name




                    frame = cv2.rectangle(frame, (int(box[0]),int(box[1])) , (int(box[2]),int(box[3])), (255,0,0), 2)
                    frame = cv2.resize(frame, (screen_width, screen_height))

        # Display the frame in full screen
        cv2.namedWindow("Camera Feed", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Camera Feed", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        # cv2.setWindowProperty("Camera Feed", cv2.WND_PROP_TOPMOST, 1)


        cv2.imshow("IMG", frame)
        cv2.waitKey(1)
        # return name



    cam.release()
    cv2.destroyAllWindows()

    if img_cropped_list is not None and name == 'Unknown':
            if not os.path.exists('photos/'+name):
                os.mkdir('photos/'+name)

            img_name = "photos/{}/{}.jpg".format(name, int(time.time()))
            cv2.imwrite(img_name, original_frame)
            print(" saved: {}".format(img_name))


def face_recog(image):
    load_data = torch.load('data.pt')
    embedding_list = load_data[0]
    name_list = load_data[1]
    cos = CosineSimilarity(dim=1)
    img_cropped_list, prob_list = mtcnn(image, return_prob=True)
    for i, prob in enumerate(prob_list):
                if prob>0.90:
                    emb = resnet(img_cropped_list[i].unsqueeze(0)).detach()

                    dist_list = [] # list of matched distances, minimum distance is used to identify the person
                    cos_sim_list = []

                    for idx, emb_db in enumerate(embedding_list):
                        dist = torch.dist(emb, emb_db).item()
                        dist_list.append(dist)
                        cos_sim = cos(emb, emb_db)
                        cos_sim = cos_sim[ 0]
                        cos_sim_list.append(cos_sim.item())


                    min_dist = min(dist_list) # get minumum dist value
                    min_dist_idx = dist_list.index(min_dist) # get minumum dist index
                    name = name_list[min_dist_idx] # get name corrosponding to minimum dist

                    print("name from min distance ", name)
                    print(min_dist)

                    # Take max cosine similarity
                    max_cos_sim = max(cos_sim_list)

                    # Get index of closest match
                    max_idx = cos_sim_list.index(max_cos_sim)

                    # Retrieve name using max index
                    name = name_list[max_idx]



                    print("name from max simaliarity ", name)
                    print(max_cos_sim)

                    # box = boxes[i]

                    original_frame = frame.copy() # storing copy of frame before drawing on it

                    if min_dist<0.90 and max_cos_sim > 0.60:
                        frame = cv2.putText(frame, name+' '+str(min_dist)+' '+str(max_cos_sim), (int(box[0]),int(box[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),1, cv2.LINE_AA)


                        text = f"Hello {name}! Welcome to Astreya"
                        # text_to_speech(name)
                        # encodings_path = "C:/Users/SahithReddy/Desktop/pytorch-facerecognition/data.pt"
                        # existing_encodings = torch.load(encodings_path)
                        # existing_embedding_list = existing_encodings[0]
                        # existing_names_list = existing_encodings[1]
                        # print("existing encodings ", existing_embedding_list)
                        # print("existing names ", existing_names_list)


                        return name
                    else:
                        frame = cv2.putText(frame, 'Unknown '+str(min_dist)+' '+str(max_cos_sim), (int(box[0]),int(box[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),1, cv2.LINE_AA)
                        name = 'Unknown'
                        return name



                    frame = cv2.rectangle(frame, (int(box[0]),int(box[1])) , (int(box[2]),int(box[3])), (255,0,0), 2)


def delete_embeddings():


  data = torch.load('data.pt')
  print("data is --",data)

  names_to_delete = ['Unknown', 'undefined', 'uploads']

  # Create a list to store indices of names to delete
  delete_idx = []

  # Iterate through names and store indices of matches
  for i, name in enumerate(data[1]):
    if name in names_to_delete:
      delete_idx.append(i)

  # Delete matches
  for idx in reversed(delete_idx):
    del data[1][idx]
    del data[0][idx]

  torch.save(data, 'data.pt')





# train_unknowns("/Users/manishcheepa/Downloads/pytorch-facerecognition/photos", "/Users/manishcheepa/Downloads/pytorch-facerecognition/data.pt" )
# if __name__ == "__main__":
#     if args.train_in_batches:
#         train_in_batches()
#     if args.train_only_unknowns:
#         train_unknowns()
#     if args.recognize:
# face_match('D:/database/frontend/Face-Recognition-frontend/src/assets/uploads/captured_image.jpg','data.pt')
# face_match()
def display_camera_fullscreen():
    # Open default camera (usually camera index 0)
    cap = cv2.VideoCapture(0)

    # Check if the camera is opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Get the default screen resolution
    screen_width = 1920  # Adjust this based on your screen resolution
    screen_height = 1080  # Adjust this based on your screen resolution

    # Set the camera frame width and height
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height)
    start_time = time.time()
    while  time.time() - start_time < 10:
        # Read a frame from the camera
        ret, frame = cap.read()

        # Check if the frame is read successfully
        if not ret:
            print("Error: Could not read frame.")
            break

        # Resize the frame to fit the screen resolution
        frame = cv2.resize(frame, (screen_width, screen_height))

        # Display the frame in full screen
        cv2.namedWindow("Camera Feed", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Camera Feed", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Camera Feed", frame)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close the OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

# Call the function to display camera feed in full screen
# display_camera_fullscreen()
# real_time_face_detection()
# face_match('C:/Users/SahithReddy/Desktop/python/src/assets/captured_image.jpg','C:/Users/SahithReddy/Desktop/python/data.pt')
# delete_embeddings()


