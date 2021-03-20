def doGreen(myGuide, myVision):
    p = {}
    q = {}

    print "Green job - Started. "

    p["x"], p["y"] = 1.5, -11.5
    q["r1"], q["r2"], q["r3"], q["r4"] = 0, 0, 0.707, 0.707
    myGuide.autoGuide(p, q, 1)

    p["x"], p["y"] = 11.25, -12.75
    q["r1"], q["r2"], q["r3"], q["r4"] = 0, 0, 0.707, -0.707
    myGuide.autoGuide(p, q, 1)

    print "Green job - Rubbish bin found. "

    p["x"], p["y"] = 1.5, 0
    q["r1"], q["r2"], q["r3"], q["r4"] = 0, 0, 0.707, 0.707
    myGuide.autoGuide(p, q)

    p["x"], p["y"] = 1.5, 0
    q["r1"], q["r2"], q["r3"], q["r4"] = 0, 0, 0.707, 0.707
    myGuide.autoGuide(p, q)

    p["x"], p["y"] = 1.5, 0
    q["r1"], q["r2"], q["r3"], q["r4"] = 0, 0, 0.707, 0.707
    myGuide.autoGuide(p, q)

    p["x"], p["y"] = 1.5, 0
    q["r1"], q["r2"], q["r3"], q["r4"] = 0, 0, 0.707, -0.707
    myGuide.autoGuide(p, q)

    print "Green job - A detour finished. "

    p["x"], p["y"] = 1, 0
    q["r1"], q["r2"], q["r3"], q["r4"] = 0, 0, 0, 1
    myGuide.autoGuide(p, q, 1)

    print "Green job - Returned to the front door. "
