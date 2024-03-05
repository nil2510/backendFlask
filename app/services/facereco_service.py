from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from torch.utils.data import DataLoader
from torchvision import datasets
import os
from PIL import Image, ImageDraw
# import cv2
from torch.nn import CosineSimilarity
from dotenv import load_dotenv


# import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument("--train", action="store_true")
# parser.add_argument("--recognize", action="store_true")
# parser.add_argument("--delete", action="store_true")
# parser.add_argument("--print", action="store_true")
# args = parser.parse_args()


load_dotenv()
IMAGE_SERVER_PATH = os.getenv('IMAGE_SERVER_PATH')

workers = 0 if os.name == 'nt' else 4
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print('Running on device: {}'.format(device))

mtcnn0 = MTCNN(image_size=240, margin=0, keep_all=False, min_face_size=40)
mtcnn = MTCNN(image_size=240, margin=0, keep_all=True, min_face_size=40)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)


def trainFace(emp_id):
    if os.path.exists('data.pt'):
        encodings = torch.load('data.pt')
        embedding_list = encodings[0]
        names_list = encodings[1]
    else:
        embedding_list = []
        names_list = []

    dataset = datasets.ImageFolder(IMAGE_SERVER_PATH + '/users')
    dataset.idx_to_class = {i:c for c, i in dataset.class_to_idx.items()}
    loader = DataLoader(dataset, collate_fn=collate_fn, num_workers=0)
    
    for img, idx in loader:
        face, prob = mtcnn0(img, return_prob=True)
        if face is not None and prob > 0.90:
            emb = resnet(face.unsqueeze(0))
            embedding_list.append(emb.detach())
            names_list.append(dataset.idx_to_class[idx])

    new_data = [embedding_list, names_list]
    print("-------------------------------- new user embedding list: ",names_list)
    torch.save(new_data, 'data.pt')

def collate_fn(x):
    return x[0]


def recogniseFace():
   img = Image.open(IMAGE_SERVER_PATH + '/captured_image/captured_image.jpg')
   boxes, _ = mtcnn.detect(img)
   if boxes is not None:
       for box in boxes:
           draw = ImageDraw.Draw(img)
           draw.rectangle(box.tolist(), outline='red', width=3)
   face, prob = mtcnn(img, return_prob=True)
   emb = resnet(face[0].unsqueeze(0)).detach()

   saved_data = torch.load('C:/Users/SunilPradhan/Desktop/Airport AMS/backendFlask/app/services/data.pt')
   embedding_list = saved_data[0]
   name_list = saved_data[1]
   dist_list = []
   cos = CosineSimilarity(dim=1)
   cos_sim_list = []

   for idx, emb_db in enumerate(embedding_list):
       dist = torch.dist(emb, emb_db).item()
       dist_list.append(dist)
       cos_sim = cos(emb, emb_db)
       cos_sim = cos_sim[ 0]
       cos_sim_list.append(cos_sim.item())

   min_dist = min(dist_list)
   min_dist_idx = dist_list.index(min_dist)
   name = name_list[min_dist_idx]

   max_cos_sim = max(cos_sim_list)
   max_idx = cos_sim_list.index(max_cos_sim)
   name = name_list[max_idx]
   print("-------------------------------- face match percentage:",max_cos_sim, "with", name)
   if min_dist<0.90 and max_cos_sim > 0.60:
       print("-------------------------------- user is recognised as",name)
       return name
   else:
       print("-------------------------------- user is recognised as Unknown")
       return 'Unknown'


def deleteFace(emp_id):
    print("-------------------------------- user embedding deleted: ",emp_id)
    data = torch.load('data.pt')
    names_to_delete = [emp_id]
    delete_idx = []
    for i, name in enumerate(data[1]):
        if name in names_to_delete:
            delete_idx.append(i)
    for idx in reversed(delete_idx):
        del data[1][idx]
        del data[0][idx]
    torch.save(data, 'data.pt')

# def deleteFace(emp_id):
#     data = torch.load('data.pt')
#     try:
#         del data[0][data[1].index(emp_id)]
#         del data[1][data[1].index(emp_id)]
#         torch.save(data, 'data.pt')
#         print("-------------------------------- user embedding deleted: ", emp_id)
#     except ValueError:
#         print("-------------------------------- user not found: ", emp_id)
    

def printFace():
    encodings = torch.load('data.pt')
    print("-------------------------------- current user embedding list: ",encodings[1])
        

# if __name__ == "__main__":
#     if args.train:
#         trainFace('E0009744')
#     if args.recognize:
#         recogniseFace()
#     if args.delete:
#         deleteFace('1')
#     if args.print:
#         printFace()
