# Class to produce random map layouts
# https://stackoverflow.com/questions/30931325/pygame-random-dungeon-generation
# http://www.roguebasin.com/index.php?title=Dungeon_builder_written_in_Python
from random import *


class dMap:
    min_room_size = (4, 4)
    max_room_size = (9, 9)

    def __init__(self):
        self.roomList = []
        self.cList = []
        self.root_wall = 1

    def makeMap(self, xsize, ysize, fail, b1, mrooms):
        """Generate random layout of rooms, corridors and other features
        fail- значение от 1 и выше. Чем выше значение неудачи, тем выше вероятность создания больших подземелий.
        Низкое значение (> 10) имеет тенденцию создавать только несколько комнат,
        высокое значение (< 50) повышает вероятность того,
        что вся область карты будет использоваться для создания комнат (вплоть до значения mrooms - см. ниже)

        b1- коридорное смещение. Это значение от 0 до 100 и представляет вероятность того, что объект будет коридором,
        а не комнатой. При значении 0 будут создаваться только комнаты, при значении 100 — только коридоры.

        mrooms - максимальное количество комнат для создания. Это, в сочетании с ошибкой, можно использовать для
        создания определенного количества комнат.

        '(0-проходимый пол, 1-пустой/необнаруженный, 2-стена, 3-открытая дверь, 4- закрытая дверь, 5-потайная дверь)'
        """

        # makeMap can be modified to accept arguments for values of failed, and percentile of features.
        # Create first room
        self.size_x = xsize
        self.size_y = ysize
        # initialize map to all walls
        self.mapArr = []
        for y in range(ysize):
            tmp = []
            for x in range(xsize):
                tmp.append(self.root_wall)
            self.mapArr.append(tmp)

        w, l, t = self.makeRoom()
        while len(self.roomList) == 0:
            try:
                y = randrange(ysize - 1 - l) + 1
                x = randrange(xsize - 1 - w) + 1
                p = self.placeRoom(l, w, x, y, xsize, ysize, 6, 0)
            except Exception as exc:
                print(exc)
                break
        failed = 0
        while failed < fail:  # The lower the value that failed< , the smaller the dungeon
            chooseRoom = randrange(len(self.roomList))
            ex, ey, ex2, ey2, et = self.makeExit(chooseRoom)
            feature = randrange(100)
            if feature < b1:  # Begin feature choosing (more features to be added here)
                w, l, t = self.makeCorridor()
            else:
                w, l, t = self.makeRoom()
            roomDone = self.placeRoom(l, w, ex2, ey2, xsize, ysize, t, et)
            if roomDone == 0:  # If placement failed increase possibility map is full
                failed += 1
            elif roomDone == 2:  # Possiblilty of linking rooms
                if self.mapArr[ey2][ex2] == 0:
                    if randrange(100) < 7:
                        self.makePortal(ex, ey)
                    failed += 1
            else:  # Otherwise, link up the 2 rooms
                self.makePortal(ex, ey)
                failed = 0
                if t < 5:
                    tc = [len(self.roomList) - 1, ex2, ey2, t]
                    self.cList.append(tc)
                    self.joinCorridor(len(self.roomList) - 1, ex2, ey2, t, 50)
            if len(self.roomList) == mrooms:
                failed = fail
        self.finalJoins()

    def makeRoom(self):
        """Randomly produce room size"""
        rtype = 5
        dsize = (self.max_room_size[0] - self.min_room_size[0], self.max_room_size[1] - self.min_room_size[1])

        rwide = min(self.size_x - 2, (randrange(dsize[0]) if dsize[0] else 0) + self.min_room_size[0])
        rlong = min(self.size_y - 2, (randrange(dsize[1]) if dsize[1] else 0) + self.min_room_size[1])
        return rwide, rlong, rtype

    def makeCorridor(self):
        """Randomly produce corridor length and heading"""
        clength = randrange(18) + 3
        heading = randrange(4)
        if heading == 0:  # North
            wd = 1
            lg = -clength
        elif heading == 1:  # East
            wd = clength
            lg = 1
        elif heading == 2:  # South
            wd = 1
            lg = clength
        elif heading == 3:  # West
            wd = -clength
            lg = 1
        return wd, lg, heading

    def placeRoom(self, ll, ww, xposs, yposs, xsize, ysize, rty, ext):
        """Place feature if enough space and return canPlace as true or false"""
        # Arrange for heading
        xpos = xposs
        ypos = yposs
        if ll < 0:
            ypos += ll + 1
            ll = abs(ll)
        if ww < 0:
            xpos += ww + 1
            ww = abs(ww)
        # Make offset if type is room
        if rty == 5:
            if ext == 0 or ext == 2:
                offset = randrange(ww)
                xpos -= offset
            else:
                offset = randrange(ll)
                ypos -= offset
        # Then check if there is space
        canPlace = 1
        if ww + xpos + 1 > xsize - 1 or ll + ypos + 1 > ysize:
            canPlace = 0
            return canPlace
        elif xpos < 1 or ypos < 1:
            canPlace = 0
            return canPlace
        else:
            for j in range(ll):
                for k in range(ww):
                    if self.mapArr[(ypos) + j][(xpos) + k] != self.root_wall:
                        canPlace = 2
        # If there is space, add to list of rooms
        if canPlace == 1:
            temp = [ll, ww, xpos, ypos]
            self.roomList.append(temp)
            for j in range(ll + 2):  # Then build walls
                for k in range(ww + 2):
                    self.mapArr[(ypos - 1) + j][(xpos - 1) + k] = 2
            for j in range(ll):  # Then build floor
                for k in range(ww):
                    self.mapArr[ypos + j][xpos + k] = 0
        return canPlace  # Return whether placed is true/false

    def makeExit(self, rn):
        """Pick random wall and random point along that wall"""
        room = self.roomList[rn]
        while True:
            rw = randrange(4)
            if rw == 0:  # North wall
                rx = randrange(room[1]) + room[2]
                ry = room[3] - 1
                rx2 = rx
                ry2 = ry - 1
            elif rw == 1:  # East wall
                ry = randrange(room[0]) + room[3]
                rx = room[2] + room[1]
                rx2 = rx + 1
                ry2 = ry
            elif rw == 2:  # South wall
                rx = randrange(room[1]) + room[2]
                ry = room[3] + room[0]
                rx2 = rx
                ry2 = ry + 1
            elif rw == 3:  # West wall
                ry = randrange(room[0]) + room[3]
                rx = room[2] - 1
                rx2 = rx - 1
                ry2 = ry
            if self.mapArr[ry][rx] == 2:  # If space is a wall, exit
                break
        return rx, ry, rx2, ry2, rw

    def makePortal(self, px, py):
        """Create doors in walls"""
        ptype = randrange(100)
        if ptype > 90:  # Secret door
            self.mapArr[py][px] = 5
            return
        elif ptype > 75:  # Closed door
            self.mapArr[py][px] = 4
            return
        elif ptype > 40:  # Open door
            self.mapArr[py][px] = 3
            return
        else:  # Hole in the wall
            self.mapArr[py][px] = 0

    def joinCorridor(self, cno, xp, yp, ed, psb):
        """Check corridor endpoint and make an exit if it links to another room"""
        cArea = self.roomList[cno]
        if xp != cArea[2] or yp != cArea[3]:  # Find the corridor endpoint
            endx = xp - (cArea[1] - 1)
            endy = yp - (cArea[0] - 1)
        else:
            endx = xp + (cArea[1] - 1)
            endy = yp + (cArea[0] - 1)
        checkExit = []
        if ed == 0:  # North corridor
            if endx > 1:
                coords = [endx - 2, endy, endx - 1, endy]
                checkExit.append(coords)
            if endy > 1:
                coords = [endx, endy - 2, endx, endy - 1]
                checkExit.append(coords)
            if endx < self.size_x - 2:
                coords = [endx + 2, endy, endx + 1, endy]
                checkExit.append(coords)
        elif ed == 1:  # East corridor
            if endy > 1:
                coords = [endx, endy - 2, endx, endy - 1]
                checkExit.append(coords)
            if endx < self.size_x - 2:
                coords = [endx + 2, endy, endx + 1, endy]
                checkExit.append(coords)
            if endy < self.size_y - 2:
                coords = [endx, endy + 2, endx, endy + 1]
                checkExit.append(coords)
        elif ed == 2:  # South corridor
            if endx < self.size_x - 2:
                coords = [endx + 2, endy, endx + 1, endy]
                checkExit.append(coords)
            if endy < self.size_y - 2:
                coords = [endx, endy + 2, endx, endy + 1]
                checkExit.append(coords)
            if endx > 1:
                coords = [endx - 2, endy, endx - 1, endy]
                checkExit.append(coords)
        elif ed == 3:  # West corridor
            if endx > 1:
                coords = [endx - 2, endy, endx - 1, endy]
                checkExit.append(coords)
            if endy > 1:
                coords = [endx, endy - 2, endx, endy - 1]
                checkExit.append(coords)
            if endy < self.size_y - 2:
                coords = [endx, endy + 2, endx, endy + 1]
                checkExit.append(coords)
        for xxx, yyy, xxx1, yyy1 in checkExit:  # Loop through possible exits
            if self.mapArr[yyy][xxx] == 0:  # If joins to a room
                if randrange(100) < psb:  # Possibility of linking rooms
                    self.makePortal(xxx1, yyy1)

    def finalJoins(self):
        """Final stage, loops through all the corridors to see if any can be joined to other rooms"""
        for x in self.cList:
            self.joinCorridor(x[0], x[1], x[2], x[3], 10)


def random_pos_in_room(room):
    return room[2] + max(0, randint(0, room[1]) - 1), room[3] + max(0, randint(0, room[0]) - 1)


def main():
    # ----------------------------------------------------------------------------
    # Main
    # ----------------------------------------------------------------------------
    startx = 20  # map width
    starty = 10  # map height
    themap = dMap()
    themap.makeMap(startx, starty, 110, 50, 60)
    for y in range(starty):
        line = ""
        for x in range(startx):
            if themap.mapArr[y][x] == 0:
                line += "."
            if themap.mapArr[y][x] == 1:
                line += " "
            if themap.mapArr[y][x] == 2:
                line += "#"
            if themap.mapArr[y][x] == 3 or themap.mapArr[y][x] == 4 or themap.mapArr[y][x] == 5:
                line += "="
        print(line)


if __name__ == '__main__':
    main()
