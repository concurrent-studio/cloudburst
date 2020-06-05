from cloudburst import vision as cbv

landmarks = cbv.get_landmarks("test.jpg")
cbv.draw_points_on_image("test.jpg", landmarks)
cbv.write_points_to_disk("test.txt", landmarks)
landmarks_from_disk = cbv.get_points_from_disk("test.txt")
print(landmarks_from_disk)
