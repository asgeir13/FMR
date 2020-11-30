import numpy as np
# import matplotlib.pyplot as plt
import pickle


def takecal(caltype, nave, nfpoints):
    S11 = np.zeros(nfpoints, dtype=np.complex128)
    # Preparing for calibration
    while True:
        resp = input(f"c to continue if your {caltype} is ready, q to quit: ")
        if resp.casefold() == "c":
            print(f"...proceeding with {caltype} calibration...")
            break
        elif resp.casefold() == "q":
            print("...program halted by user!!!")
            # leave system in safe mode, magnet etc.
            quit()
        else:
            print("The only responses to exit this loop are c and q!")

    while True:
        # loop over nave, do the calibration
        S11 = (np.random.random() + 1j) * np.ones(nfpoints)
        # enddo the calibration
        resp = input("r to repeat calibration, c to continue, q to quit: ")
        if resp.casefold() == "c":
            print("Your choice was: " + resp)
            print("(" + resp + ")")
            break
        elif resp.casefold() == "r":
            print(f"Repeating {caltype} calibration, your choice was: " + resp)
            print("(" + resp + ")")
            # reinitialize the vectors
            S11 = np.zeros(nfpoints)
        elif resp.casefold() == "q":
            print("...program halted by user!!!")
            # leave system in safe mode, magnet etc.
            quit()
        else:
            print("your options are C(ontinue)/R(epeat)/Q(uit)...")

    return S11


def calcorr(S11s, S11o, S11l):
    print("Calculating correction coefficients, the E's")
    Edf = S11l
    Erf = 2 * (S11o - S11l) * (S11l - S11s)/(S11o - S11s)
    Esf = (S11o - S11s - 2 * S11l)/(S11o - S11s)
    return Edf, Erf, Esf


def docal(S11m, Edf, Erf, Esf):
    print("Calculating correction for given S11.")
    Z0 = 50
    S11a = (S11m - Edf)/((S11m - Edf) * Esf + Erf)
    Za = Z0 * (1 + S11a)/(1 - S11a)
    return S11a, Za


# set some initial values
nfpoints = 6
nave = 10
S11o = S11l = S11s = np.zeros(nfpoints, dtype=np.complex128)
S11a = S11m = Za = np.zeros(nfpoints, dtype=np.complex128)
Edf = Erf = Esf = np.zeros(nfpoints, dtype=np.complex128)
freq = np.zeros(nfpoints, dtype=np.float64)

S11o = takecal("OPEN", nave, nfpoints)
S11l = takecal("LOAD", nave, nfpoints)
# prepare magnetic field for short measurement
S11s = takecal("SHORT", nave, nfpoints)
Edf, Erf, Esf = calcorr(S11s, S11o, S11l)
# do actual measurement(s) ==> S11m measurement
S11m = (np.random.random(nfpoints) + 1j*np.random.random(nfpoints))
S11a, Za = docal(S11m, Edf, Erf, Esf)
Resist = Za.real
React = Za.imag
# data = {"a": 1, "b": 2, "calib": S11li, "name": 'Snorri'}
# afile = open("data.pkl", "wb")
# pickle.dump(data, afile)
# afile.close()
# # afile = open("data.pkl", "rb")
# # output = pickle.load(afile)
# # print(output)
# # afile.close

# gd goto definition, e.g. go to the function name under cursor
# ]M or [M goto end or beginning of method (function)
