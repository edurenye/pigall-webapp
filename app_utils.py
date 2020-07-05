import numpy as np
import math
import time


def update_current_objects(current_objects, predictions):
    now = time.time()
    for prediction in predictions:
        object_type = prediction[0]
        if object_type == 'traffic_light':
            continue
        else:
            found = False
            for current_object_type in current_objects:
                for current_object in current_objects[current_object_type]:
                    if are_the_same(current_object_type, current_object, prediction):
                        found = True
                        current_object['last_appearance'] = now
                        current_object['counter'] += 1
                        current_object['bounding_boxes'].append(prediction[1])
            if not found:
                current_objects[object_type].append({
                    'last_appearance': now,
                    'counter': 1,
                    'bounding_boxes': [prediction[1]]
                })
    for key in current_objects:
        for current_object in current_objects[key]:
            if current_object['last_appearance'] < (now - 2):
                current_objects[key].remove(current_object)


def are_the_same(current_object_type, current_object, prediction):
    pedestrian_tl = ['pedestrian_green', 'pedestrian_off', 'pedestrian_red']
    if current_object_type == prediction[0] or (current_object_type in pedestrian_tl and prediction[0] in pedestrian_tl):
        cx = current_object['bounding_boxes'][-1][0]
        cy = current_object['bounding_boxes'][-1][1]
        px = prediction[1][0]
        py = prediction[1][1]
        dist = math.sqrt((px - cx)**2 + (py - cy)**2)
        if dist < 20:
            return True
    return False


def get_dangers(danger_detector, current_objects, size):
    dangers = []
    for current_object_type in current_objects:
        for current_object in current_objects[current_object_type]:
            if current_object['counter'] > 10:
                growth = get_growth(current_object['bounding_boxes'])
                position = get_position(current_object['bounding_boxes'][-1], size)
                danger = danger_detector.get_danger(current_object_type, growth, position)
                if current_object_type == 'pedestrian_green':
                    danger = danger / 2
                print('Danger: ', current_object_type, danger)
                dangers.append([current_object_type, danger, current_object['bounding_boxes'][-1]])
    return dangers


def get_growth(bounding_boxes):
    first = bounding_boxes[0]
    last = bounding_boxes[-1]
    first_diagonal = math.sqrt(first[2] ** 2 + first[3] ** 2)
    last_diagonal = math.sqrt(last[2] ** 2 + last[3] ** 2)
    diagonal_increment = last_diagonal - first_diagonal
    ratio = (diagonal_increment / first_diagonal) * 40
    ratio = np.clip(ratio, 0, 10)
    print('Growth: ', ratio)
    return ratio


def get_position(xywh, size):
    center = xywh[0] + (float(xywh[2]) / 2)
    position = (center / size) * 10
    return position
