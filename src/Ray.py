from math import sqrt

from pygame import Vector2


def get_line(start, end):
    """Bresenham's Line Algorithm
    Produces a list of tuples from start and end
    >>> points1 = get_line((0, 0), (3, 4))
    >>> points2 = get_line((3, 4), (0, 0))
    >>> assert(set(points1) == set(points2))
    >>> print points1
    [(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]
    >>> print points2
    [(3, 4), (2, 3), (1, 2), (1, 1), (0, 0)]
    """
    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points


def raycast_DDA(vPlayer, vMouse, cellSize, vMapSize, arrMap, walls={2, 4, 5}, offset_dist=0, fMaxDistance=30):
    # https://github.com/OneLoneCoder/Javidx9/blob/master/PixelGameEngine/SmallerProjects/OneLoneCoder_PGE_RayCastDDA.cpp
    # DDA Algorithm ==============================================
    # https://lodev.org/cgtutor/raycasting.html

    # Form ray cast from player into scene
    vRayDir = (vMouse - vPlayer).normalize()

    vPlayer /= cellSize
    vRayStart = vPlayer

    # Lodev.org also explains this additional optimistaion (but it's beyond scope of video)
    # olc::vf2d vRayUnitStepSize = { abs(1.0f / vRayDir.x), abs(1.0f / vRayDir.y) }

    dyx = (vRayDir.y / vRayDir.x) if vRayDir.x != 0 else 0
    dxy = (vRayDir.x / vRayDir.y) if vRayDir.y != 0 else 0
    # vRayUnitStepSize = Vector2(sqrt(1 + (dyx) * (dyx)),
    #                            sqrt(1 + (dxy) * (dxy)))
    vRayUnitStepSize = Vector2(abs(1.0 / vRayDir.x) if vRayDir.x != 0 else 1e30
                               , abs(1.0 / vRayDir.y) if vRayDir.y != 0 else 1e30)

    vMapCheck = Vector2(vRayStart)
    vRayLength1D = Vector2()
    vStep = Vector2()

    # Establish Starting Conditions
    if (vRayDir.x < 0):
        vStep.x = -1
        vRayLength1D.x = (vRayStart.x - int(vMapCheck.x)) * vRayUnitStepSize.x
    else:
        vStep.x = 1
        vRayLength1D.x = (int(vMapCheck.x + 1) - vRayStart.x) * vRayUnitStepSize.x

    if (vRayDir.y < 0):
        vStep.y = -1
        vRayLength1D.y = (vRayStart.y - int(vMapCheck.y)) * vRayUnitStepSize.y
    else:
        vStep.y = 1
        vRayLength1D.y = (int(vMapCheck.y + 1) - vRayStart.y) * vRayUnitStepSize.y

    # Perform "Walk" until collision or range check

    bTileFound = False
    lstTilesFound = set()

    last_tile = (0, 0)
    fDistance = 0.0
    while (not bTileFound) and (fDistance < fMaxDistance):
        # Walk along shortest path
        if (vRayLength1D.x < vRayLength1D.y):

            vMapCheck.x += vStep.x
            fDistance = vRayLength1D.x
            vRayLength1D.x += vRayUnitStepSize.x

        else:

            vMapCheck.y += vStep.y
            fDistance = vRayLength1D.y
            vRayLength1D.y += vRayUnitStepSize.y

        # Test tile at new test point
        if fDistance > fMaxDistance:
            fDistance = fMaxDistance
            break
        coord = (int(vMapCheck.x), int(vMapCheck.y))
        if 0 <= vMapCheck[0] < vMapSize.x and 0 <= vMapCheck[1] < vMapSize.y:
            # print((vMapCheck-vRayStart).length(), fMaxDistance)
                lstTilesFound.add(coord)
                if arrMap[int(vMapCheck.y)][int(vMapCheck.x)] in walls:
                    bTileFound = True
                    last_tile = coord

    # Calculate intersection location
    vIntersection = Vector2()
    if (bTileFound or 1):
        vIntersection = vRayDir * (fDistance - offset_dist)

    return lstTilesFound, vIntersection, last_tile
