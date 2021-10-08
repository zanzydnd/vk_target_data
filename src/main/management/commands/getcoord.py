from django.core.management import BaseCommand
from main.management.admin_coord import coordinates
from main.models import Coord


def point_in_poly(p, poly):
    x, y = p
    odd = False

    for segment_a, segment_b in zip(poly, poly[1:] + [poly[0]]):
        x_a, y_a = segment_a
        x_b, y_b = segment_b
        if (y_a < y <= y_b) or (y_b < y <= y_a):
            if (x_a + (y - y_a) / (y_b - y_a) * (x_b - x_a)) < x:
                odd = not odd

    return odd


class Command(BaseCommand):

    def handle(self, *args, **options):
        min_x = coordinates[0][0][0][0]
        min_y = coordinates[0][0][0][1]
        max_x = 0.0
        max_y = 0.0
        for i in range(len(coordinates)):
            for j in range(len(coordinates[i][0])):
                if coordinates[i][0][j][0] < min_x:
                    min_x = coordinates[i][0][j][0]
                if coordinates[i][0][j][0] > max_x:
                    max_x = coordinates[i][0][j][0]
                if coordinates[i][0][j][1] < min_y:
                    min_y = coordinates[i][0][j][1]
                if coordinates[i][0][j][1] > max_y:
                    max_y = coordinates[i][0][j][1]
        x, y = min_x, min_y
        d_x = (max_x - min_x) / (75 * 2)
        d_y = (max_y - min_y) / (98 * 2)
        counter = 0

        data = []

        while max_x >= x:
            x += d_x
            while max_y >= y:
                y += d_y
                for i in range(len(coordinates)):
                    if point_in_poly([x, y], coordinates[i][0]):
                        counter += 1
                        data.append(Coord(x=x, y=y))
            y = min_y

        Coord.objects.bulk_create(data)
