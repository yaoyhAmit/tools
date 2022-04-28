import numpy as np
import matplotlib.pyplot as plt
import csv
from datetime import datetime
import argparse

class LinearInterpolation():
    def __init__(self, name='Linear', q_via=None, t_via=None):
        """
        :param: name: string
            name of objective
        :param: q_via: N x 3 array
            given q array
        :param: t_via: N x 1 array
            given t array
        """
        super(self.__class__, self).__init__()
        self.name = name
        self.q_via = q_via
        self.t_via = t_via

        try:
            q_via.shape[1] != t_via.shape[0]
        except ValueError:
            print('The q_via and t_via must have a same length')

    def linear(self, q0, q1, t0, t1):
        """
        :param: q0: float
            the first data point
        :param: q1: float
            the second data point
        :param: t0: float
            the time of the first data point
        :param: t1: float
            the time of the second data point
        """
        try:
            abs(t0 - t1) < 1e-6
        except ValueError:
            print('t0 and t1 must be different')

        a0 = q0
        a1 = (q1 - q0)/(t1 - t0)
        return a0, a1

    def getPosition(self, t):
        """
        :param: t: float
            specified time
        :return: q: float
            output of the interpolation at time t
        """
        try:
            (t < self.t_via[0]) or (t > self.t_via[-1])
        except ValueError:
            print('The specific time error, time ranges error')

        j_array = np.where(self.t_via >= t) # find the index of t1
        j = j_array[0][0]
        if j == 0:
            i = 0
            j = 1
        else:
            i = j-1

        q = np.zeros((1, 3))

        # position
        q0 = self.q_via[i,0]
        t0 = self.t_via[i]
        q1 = self.q_via[j,0]
        t1 = self.t_via[j]
        a0, a1 = self.linear(q0, q1, t0, t1)
        q[0, 0] = a0 + a1*(t - t0)

        # velocity
        q[0, 1] = a1

        # acceleration
        q[0, 2] = 0 # for linear model, the acceleration is infinite, here we set to zero
        return q

        
class ParabolicInterpolation():
    def __init__(self, name='Parabolic', q_via=None, t_via=None):
        """
        :param: name: string
            name of objective
        :param: q_via: N x 3 array
            given q array
        :param: t_via: N x 1 array
            given t array
        """
        super(self.__class__, self).__init__()
        self.name = name
        self.q_via = q_via
        self.t_via = t_via

        try:
            q_via.shape[1] != t_via.shape[0]
        except ValueError:
            print('The q_via and t_via must have a same length')

    def parabolic(self, q0, q1, v0, v1, t0, t1, tf, qf):
        """
        :param: q0: float
            the first data point
        :param: q1: float
            the second data point
        :param: v0: float
            the velocity of the first data point
        :param: v1: float
            the velocity of the second data point
        :param: t0: float
            the time of the first data point
        :param: t1: float
            the time of the second data point
        :param: tf: float
            the time of the flex point
        :param: qf: float
            the position of the flex point
        """
        
        try:
            abs(t0 - t1) < 1e-6
        except ValueError:
                print('t0 and t1 must be different')

        try:
            ((tf <= t0) or (tf >= t1))
        except ValueError:
            print('tf must satisfy t0 < tf < t1')

        try:
            ((qf <= min(q0, q1)) or (qf >= max(q0, q1)))
        except ValueError:
            print('qf must satisfy min(q0, q1) < qf < max(q0, q1)')

        T = t1 - t0
        h = q1 - q0
        Ta = tf - t0
        Td = t1 - tf

        a0 = q0
        a1 = v0
        a2 = (2*h - v0*(T + Ta) - v1*Td)/(2*T*Ta)
        a3 = (2*q1*Ta + Td*(2*q0 + Ta*(v0 - v1)))/(2*T)
        a4 = (2*h - v0*Ta - v1*Td)/T
        a5 = -(2*h - v0*Ta - v1*(T+Td))/(2*T*Td)
        return a0, a1, a2, a3, a4, a5

    def getPosition(self, t):
        """
        :param: t: float
            specified time
        :return: q: float
            output of the interpolation at time t
        """
        try:
            (t < self.t_via[0]) or (t > self.t_via[-1])
        except ValueError:
            print('The specific time error, time ranges error')

        j_array = np.where(self.t_via >= t) # find the index of t1
        j = j_array[0][0]
        if j == 0:
            i = 0
            j = 1
        else:
            i = j-1

        q = np.zeros((1, 3))

        # get given position
        q0 = self.q_via[i,0]
        v0 = self.q_via[i,1]
        t0 = self.t_via[i]

        q1 = self.q_via[j,0]
        v1 = self.q_via[j,1]
        t1 = self.t_via[j]

        # symmetric acceleration
        tf = (t0 + t1)/2
        qf = (q0 + q1)/2

        # asymmetric acceleration, specify tf and qf by users
        # tf = ?
        # qf = ?

        a0, a1, a2, a3, a4, a5 = self.parabolic(q0, q1, v0, v1, t0, t1, tf, qf)

        if t <= tf:
            q[0, 0] = a0 + a1*(t - t0) + a2*(t-t0)**2
            q[0, 1] = a1 + 2*a2*(t - t0)
            q[0, 2] = 2*a2
        else:
            q[0, 0] = a3 + a4*(t - tf) + a5*(t-tf)**2
            q[0, 1] = a4 + 2*a5*(t - tf)
            q[0, 2] = 2*a5

        return q


class CubicInterpolation():
    def __init__(self, name='Cubic', x_via=None, y_via=None,  z_via=None,  rx_via=None, ry_via=None,  rz_via=None, t_via=None):
        """
        :param: name: string
            name of objective
        :param: x_via: N x 3 array
            given x array
        :param: y_via: N y 3 array
            given y array
        :param: z_via: N z 3 array
            given x array
        :param: rx_via: N x 3 array
            given rx array
        :param: ry_via: N ry 3 array
            given ry array
        :param: rz_via: N rz 3 array
            given rx array
        :param: t_via: N x 1 array
            given t array
        """
        super(self.__class__, self).__init__()
        self.name = name
        self.x_via = x_via
        self.y_via = y_via
        self.z_via = z_via
        self.rx_via = rx_via
        self.ry_via = ry_via
        self.rz_via = rz_via
        self.t_via = t_via

        try:
            x_via.shape[1] != t_via.shape[0]
            y_via.shape[1] != t_via.shape[0]
            z_via.shape[1] != t_via.shape[0]
            rx_via.shape[1] != t_via.shape[0]
            ry_via.shape[1] != t_via.shape[0]
            rz_via.shape[1] != t_via.shape[0]
        except ValueError:
            print('The via and t_via must have a same length')

    def cubic(self, q0, q1, v0, v1, t0, t1):
        """
        :param: q0: float
            the first data point
        :param: q1: float
            the second data point
        :param: v0: float
            the velocity of the first data point
        :param: v1: float
            the velocity of the second data point
        :param: t0: float
            the time of the first data point
        :param: t1: float
            the time of the second data point
        """
        try:
            abs(t0 - t1) < 1e-6
        except ValueError:
                print('t0 and t1 must be different')


        T = t1 - t0
        h = q1 - q0

        a0 = q0
        a1 = v0
        a2 = (3*h - (2*v0 + v1)*T) / (T**2)
        a3 = (-2*h + (v0 + v1)*T) / (T**3)
        return a0, a1, a2, a3

    def getPosition(self, t,):
        """
        :param: t: float
            specified time
        :return: q: float
            output of the interpolation at time t
        """
        try:
            (t < self.t_via[0]) or (t > self.t_via[-1])
        except ValueError:
            print('The specific time error, time ranges error')

        j_array = np.where(self.t_via >= t) # find the index of t1
        j = j_array[0][0]
        if j == 0:
            i = 0
            j = 1
        else:
            i = j-1

        x = np.zeros((1, 3))
        y = np.zeros((1, 3))
        z = np.zeros((1, 3))
        rx = np.zeros((1, 3))
        ry = np.zeros((1, 3))
        rz = np.zeros((1, 3))

        # get given position
        q0 = self.x_via[i,0]
        v0 = self.x_via[i,1]
        t0 = self.t_via[i]

        q1 = self.x_via[j,0]
        v1 = self.x_via[j,1]
        t1 = self.t_via[j]

        a0, a1, a2, a3 = self.cubic(q0, q1, v0, v1, t0, t1)

        x[0, 0] = a0 + a1*(t - t0) + a2*(t-t0)**2 + a3*(t - t0)**3 # position
        x[0, 1] = a1 + 2*a2*(t - t0) + 3*a3*(t - t0)**2 # velocity
        x[0, 2] = 2*a2 + 6*a3*(t - t0) # acceleration

        # get given position
        q0 = self.y_via[i,0]
        v0 = self.y_via[i,1]
        t0 = self.t_via[i]

        q1 = self.y_via[j,0]
        v1 = self.y_via[j,1]
        t1 = self.t_via[j]

        a0, a1, a2, a3 = self.cubic(q0, q1, v0, v1, t0, t1)

        y[0, 0] = a0 + a1*(t - t0) + a2*(t-t0)**2 + a3*(t - t0)**3 # position
        y[0, 1] = a1 + 2*a2*(t - t0) + 3*a3*(t - t0)**2 # velocity
        y[0, 2] = 2*a2 + 6*a3*(t - t0) # acceleration

        # get given position
        q0 = self.z_via[i,0]
        v0 = self.z_via[i,1]
        t0 = self.t_via[i]

        q1 = self.z_via[j,0]
        v1 = self.z_via[j,1]
        t1 = self.t_via[j]

        a0, a1, a2, a3 = self.cubic(q0, q1, v0, v1, t0, t1)

        z[0, 0] = a0 + a1*(t - t0) + a2*(t-t0)**2 + a3*(t - t0)**3 # position
        z[0, 1] = a1 + 2*a2*(t - t0) + 3*a3*(t - t0)**2 # velocity
        z[0, 2] = 2*a2 + 6*a3*(t - t0) # acceleration

        # get given position
        q0 = self.rx_via[i,0]
        v0 = self.rx_via[i,1]
        t0 = self.t_via[i]

        q1 = self.rx_via[j,0]
        v1 = self.rx_via[j,1]
        t1 = self.t_via[j]

        a0, a1, a2, a3 = self.cubic(q0, q1, v0, v1, t0, t1)

        rx[0, 0] = a0 + a1*(t - t0) + a2*(t-t0)**2 + a3*(t - t0)**3 # position
        rx[0, 1] = a1 + 2*a2*(t - t0) + 3*a3*(t - t0)**2 # velocity
        rx[0, 2] = 2*a2 + 6*a3*(t - t0) # acceleration

        # get given position
        q0 = self.ry_via[i,0]
        v0 = self.ry_via[i,1]
        t0 = self.t_via[i]

        q1 = self.ry_via[j,0]
        v1 = self.ry_via[j,1]
        t1 = self.t_via[j]

        a0, a1, a2, a3 = self.cubic(q0, q1, v0, v1, t0, t1)

        ry[0, 0] = a0 + a1*(t - t0) + a2*(t-t0)**2 + a3*(t - t0)**3 # position
        ry[0, 1] = a1 + 2*a2*(t - t0) + 3*a3*(t - t0)**2 # velocity
        ry[0, 2] = 2*a2 + 6*a3*(t - t0) # acceleration

        # get given position
        q0 = self.rz_via[i,0]
        v0 = self.rz_via[i,1]
        t0 = self.t_via[i]

        q1 = self.rz_via[j,0]
        v1 = self.rz_via[j,1]
        t1 = self.t_via[j]

        a0, a1, a2, a3 = self.cubic(q0, q1, v0, v1, t0, t1)

        rz[0, 0] = a0 + a1*(t - t0) + a2*(t-t0)**2 + a3*(t - t0)**3 # position
        rz[0, 1] = a1 + 2*a2*(t - t0) + 3*a3*(t - t0)**2 # velocity
        rz[0, 2] = 2*a2 + 6*a3*(t - t0) # acceleration

        return x, y, z, rx, ry, rz


class Polynomial5Interpolation():
    def __init__(self, name='Polynomial 5', x_via=None,  y_via=None, z_via=None,  rx_via=None,  ry_via=None, rz_via=None, t_via=None):
        """
        :param: name: string
            name of objective
        :param: q_via: N x 3 array
            given q array
        :param: t_via: N x 1 array
            given t array
        """
        super(self.__class__, self).__init__()
        self.name = name
        self.x_via = x_via
        self.y_via = y_via
        self.z_via = z_via
        self.rx_via = rx_via
        self.ry_via = ry_via
        self.rz_via = rz_via
        self.t_via = t_via

        try:
            x_via.shape[1] != t_via.shape[0]
            y_via.shape[1] != t_via.shape[0]
            z_via.shape[1] != t_via.shape[0]
            rx_via.shape[1] != t_via.shape[0]
            ry_via.shape[1] != t_via.shape[0]
            rz_via.shape[1] != t_via.shape[0]
        except ValueError:
            print('The q_via and t_via must have a same length')

    def polynomial(self, q0, q1, v0, v1, acc0, acc1, t0, t1):
        """
        :param: q0: float
            the first data point
        :param: q1: float
            the second data point
        :param: v0: float
            the velocity of the first data point
        :param: v1: float
            the velocity of the second data point
        :param: acc0: float
            the acceleration of the first data point
        :param: acc1: float
            the acceleration of the second data point
        :param: t0: float
            the time of the first data point
        :param: t1: float
            the time of the second data point
        """
        try:
            abs(t0 - t1) < 1e-6
        except ValueError:
                print('t0 and t1 must be different')


        T = t1 - t0
        h = q1 - q0

        a0 = q0
        a1 = v0
        a2 = acc0/2
        a3 = (20*h - (8*v1 + 12*v0)*T - (3*acc0 - acc1)*T**2) / (2*T**3)
        a4 = (-30*h + (14*v1 + 16*v0)*T + (3*acc0 - 2*acc1)*T**2) / (2*T**4)
        a5 = (12*h - 6*(v1 + v0)*T + (acc1 - acc0)*T**2) / (2*T**5)
        return a0, a1, a2, a3, a4, a5

    def getPosition(self, t):
        """
        :param: t: float
            specified time
        :return: q: float
            output of the interpolation at time t
        """
        try:
            (t < self.t_via[0]) or (t > self.t_via[-1])
        except ValueError:
            print('The specific time error, time ranges error')

        j_array = np.where(self.t_via >= t) # find the index of t1
        # j_array = np.where(self.t_via < -1) # find the index of t1
        if len(j_array[0]) <= 0:
            return None,None,None,None,None,None

        j = j_array[0][0]
        if j == 0:
            i = 0
            j = 1
        else:
            i = j-1

        x = np.zeros((1, 3))
        y = np.zeros((1, 3))
        z = np.zeros((1, 3))

        rx = np.zeros((1, 3))
        ry = np.zeros((1, 3))
        rz = np.zeros((1, 3))

        # get given position
        q0 = self.x_via[i,0]
        v0 = self.x_via[i,1]
        acc0 = self.x_via[i,2]
        t0 = self.t_via[i]

        q1 = self.x_via[j,0]
        v1 = self.x_via[j,1]
        acc1 = self.x_via[j,2]
        t1 = self.t_via[j]

        a0, a1, a2, a3, a4, a5 = self.polynomial(q0, q1, v0, v1, acc0, acc1, t0, t1)

        x[0, 0] = a0 + a1*(t - t0) + a2*(t-t0)**2 + a3*(t - t0)**3 + a4*(t -  t0)**4 + a5*(t - t0)**5 # position
        x[0, 1] = a1 + 2*a2*(t - t0) + 3*a3*(t - t0)**2 + 4*a4*(t - t0)**3 + 5*a5*(t - t0)**4 # velocity
        x[0, 2] = 2*a2 + 6*a3*(t - t0) + 12*a4*(t- t0)**2 + 20*a5*(t - t0)**3 # acceleration

        # get given position
        q0 = self.y_via[i,0]
        v0 = self.y_via[i,1]
        acc0 = self.y_via[i,2]
        t0 = self.t_via[i]

        q1 = self.y_via[j,0]
        v1 = self.y_via[j,1]
        acc1 = self.y_via[j,2]
        t1 = self.t_via[j]

        a0, a1, a2, a3, a4, a5 = self.polynomial(q0, q1, v0, v1, acc0, acc1, t0, t1)

        y[0, 0] = a0 + a1*(t - t0) + a2*(t-t0)**2 + a3*(t - t0)**3 + a4*(t -  t0)**4 + a5*(t - t0)**5 # position
        y[0, 1] = a1 + 2*a2*(t - t0) + 3*a3*(t - t0)**2 + 4*a4*(t - t0)**3 + 5*a5*(t - t0)**4 # velocity
        y[0, 2] = 2*a2 + 6*a3*(t - t0) + 12*a4*(t- t0)**2 + 20*a5*(t - t0)**3 # acceleration

        # get given position
        q0 = self.z_via[i,0]
        v0 = self.z_via[i,1]
        acc0 = self.z_via[i,2]
        t0 = self.t_via[i]

        q1 = self.z_via[j,0]
        v1 = self.z_via[j,1]
        acc1 = self.z_via[j,2]
        t1 = self.t_via[j]

        a0, a1, a2, a3, a4, a5 = self.polynomial(q0, q1, v0, v1, acc0, acc1, t0, t1)

        z[0, 0] = a0 + a1*(t - t0) + a2*(t-t0)**2 + a3*(t - t0)**3 + a4*(t -  t0)**4 + a5*(t - t0)**5 # position
        z[0, 1] = a1 + 2*a2*(t - t0) + 3*a3*(t - t0)**2 + 4*a4*(t - t0)**3 + 5*a5*(t - t0)**4 # velocity
        z[0, 2] = 2*a2 + 6*a3*(t - t0) + 12*a4*(t- t0)**2 + 20*a5*(t - t0)**3 # acceleration        

        # get given position
        q0 = self.rx_via[i,0]
        v0 = self.rx_via[i,1]
        acc0 = self.rx_via[i,2]
        t0 = self.t_via[i]

        q1 = self.rx_via[j,0]
        v1 = self.rx_via[j,1]
        acc1 = self.rx_via[j,2]
        t1 = self.t_via[j]

        a0, a1, a2, a3, a4, a5 = self.polynomial(q0, q1, v0, v1, acc0, acc1, t0, t1)

        rx[0, 0] = a0 + a1*(t - t0) + a2*(t-t0)**2 + a3*(t - t0)**3 + a4*(t -  t0)**4 + a5*(t - t0)**5 # position
        rx[0, 1] = a1 + 2*a2*(t - t0) + 3*a3*(t - t0)**2 + 4*a4*(t - t0)**3 + 5*a5*(t - t0)**4 # velocity
        rx[0, 2] = 2*a2 + 6*a3*(t - t0) + 12*a4*(t- t0)**2 + 20*a5*(t - t0)**3 # acceleration

        # get given position
        q0 = self.ry_via[i,0]
        v0 = self.ry_via[i,1]
        acc0 = self.ry_via[i,2]
        t0 = self.t_via[i]

        q1 = self.ry_via[j,0]
        v1 = self.ry_via[j,1]
        acc1 = self.ry_via[j,2]
        t1 = self.t_via[j]

        a0, a1, a2, a3, a4, a5 = self.polynomial(q0, q1, v0, v1, acc0, acc1, t0, t1)

        ry[0, 0] = a0 + a1*(t - t0) + a2*(t-t0)**2 + a3*(t - t0)**3 + a4*(t -  t0)**4 + a5*(t - t0)**5 # position
        ry[0, 1] = a1 + 2*a2*(t - t0) + 3*a3*(t - t0)**2 + 4*a4*(t - t0)**3 + 5*a5*(t - t0)**4 # velocity
        ry[0, 2] = 2*a2 + 6*a3*(t - t0) + 12*a4*(t- t0)**2 + 20*a5*(t - t0)**3 # acceleration

        # get given position
        q0 = self.rz_via[i,0]
        v0 = self.rz_via[i,1]
        acc0 = self.rz_via[i,2]
        t0 = self.t_via[i]

        q1 = self.rz_via[j,0]
        v1 = self.rz_via[j,1]
        acc1 = self.rz_via[j,2]
        t1 = self.t_via[j]

        a0, a1, a2, a3, a4, a5 = self.polynomial(q0, q1, v0, v1, acc0, acc1, t0, t1)

        rz[0, 0] = a0 + a1*(t - t0) + a2*(t-t0)**2 + a3*(t - t0)**3 + a4*(t -  t0)**4 + a5*(t - t0)**5 # position
        rz[0, 1] = a1 + 2*a2*(t - t0) + 3*a3*(t - t0)**2 + 4*a4*(t - t0)**3 + 5*a5*(t - t0)**4 # velocity
        rz[0, 2] = 2*a2 + 6*a3*(t - t0) + 12*a4*(t- t0)**2 + 20*a5*(t - t0)**3 # acceleration

        return x, y, z, rx, ry, rz

def readUSTSCSV(csvfile,t0_dt,t0_ms):
    msOffset = 416
    with open(csvfile) as csv_file:
        csv_reader = list(csv.reader(csv_file,delimiter=','))
        row_count = len(csv_reader)
        line_count = 0
        ti_sum = 0
        ti_avg = 0
        ti_tmp = 0

        t_us = np.zeros(row_count)

        for row in csv_reader:
            line_count += 1
            ts = row[0]
            if len(ts.split(',')) > 1:
                timeStamp = ts.split(',')[0]
                ms = int(ts.split(',')[1])
                dt = datetime.strptime(timeStamp,'%Y/%m/%d %H:%M:%S')
                ti = (dt - t0_dt).total_seconds() * 1000 + (ms - t0_ms)
            elif len(row) > 1:
                timeStamp = row[0]
                ms = int(row[1])
                dt = datetime.strptime(timeStamp,'%Y/%m/%d %H:%M:%S')
                ti = (dt - t0_dt).total_seconds() * 1000 + (ms - t0_ms)
            else:
                ti = ti_tmp + ti_avg
            
            t_us[line_count-1] = ti - msOffset

            ti_sum = ti_sum + (ti - ti_tmp)
            ti_avg = round(ti_sum/line_count,0)
            ti_tmp = ti

        return t_us

def readTrackCSV(csvfile):
    with open(csvfile) as csv_file:
        csv_reader = list(csv.reader(csv_file,delimiter=','))
        row_count = len(csv_reader)
        line_count = 0
        t0_dt = None
        t0_ms = None
        
        x_given = np.zeros((row_count-1,3))
        y_given = np.zeros((row_count-1,3))
        z_given = np.zeros((row_count-1,3))
        rx_given = np.zeros((row_count-1,3))
        ry_given = np.zeros((row_count-1,3))
        rz_given = np.zeros((row_count-1,3))
        t_given = np.zeros(row_count-1)

        for row in csv_reader:
            line_count += 1
            if line_count == 1:
                continue
            else:
                id = row[0]
                x = float(row[1])
                y = float(row[2])
                z = float(row[3])
                rx = float(row[4])
                ry = float(row[5])
                rz = float(row[6])
                timeStamp = row[28].split(' ')[0] + ' ' + row[28].split(' ')[1]
                ms = int(row[28].split(' ')[2])
                dt = datetime.strptime(timeStamp,'%Y/%m/%d %H:%M:%S')
                if t0_dt is None:
                    t0_dt = dt
                    t0_ms = ms
                    ti = 0
                else:
                    ti = (dt - t0_dt).total_seconds() * 1000 + (ms - t0_ms)
                
                x_given[line_count-2,0] = x
                y_given[line_count-2,0] = y
                z_given[line_count-2,0] = z
                rx_given[line_count-2,0] = rx
                ry_given[line_count-2,0] = ry
                rz_given[line_count-2,0] = rz
                t_given[line_count-2] = ti

            if line_count >= row_count:
                break
        
        return x_given, y_given, z_given, rx_given, ry_given, rz_given, t_given, t0_dt, t0_ms



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='computing position csv file')
    
    parser.add_argument('--inCSV', required=True, help='dinan track file path')
    parser.add_argument('--inUSTS', required=True, help='us time stamp')
    parser.add_argument('--outCSV', required=True, help='out put csv file')

    args = parser.parse_args()

    inCSV = args.inCSV
    inUSTS = args.inUSTS
    outCSV = args.outCSV
    # q_given = np.array([[0, 1.6, 3.2, 2, 4, 0.2, 1.2],
    #                     [0, 1.0, 2.0, -2.0, -1.0, 0, 0],
    #                     [0, 1, 2, 3, 2, 1, 0]]).transpose()
    # q_given = np.array([[0, 1.6, 3.2, 2, 4, 0.2, 1.2],
    #                     [0, 0, 0, 0, 0, 0, 0],
    #                     [0, 0, 0, 0, 0, 0, 0]]).transpose()


    # t_given = np.array([0, 1, 3, 4.5, 6, 8, 10]).transpose()

    x_given,y_given,z_given,dx_given,dy_given,dz_given,t_given,t0_dt,t0_ms = readTrackCSV(inCSV)
    
    t_us = readUSTSCSV(inUSTS,t0_dt,t0_ms)

    # time for interpolation
    # t = np.linspace(t_given[0], t_given[-1], 1000)
    count = int(t_given[-1]-t_given[0])
    t = np.linspace(t_given[0], t_given[-1], count)

    # write csv file
    polynomial5_interpolation = Polynomial5Interpolation('Polynomial5', x_given,  y_given, z_given,  dx_given,  dy_given, dz_given, t_given)
    polynomial5_trajectory_x = np.zeros((1, 3)) # N x 3 array: position, velocity, acceleration
    polynomial5_trajectory_y = np.zeros((1, 3)) # N x 3 array: position, velocity, acceleration
    polynomial5_trajectory_z = np.zeros((1, 3)) # N x 3 array: position, velocity, acceleration
    polynomial5_trajectory_dx = np.zeros((1, 3)) # N x 3 array: position, velocity, acceleration
    polynomial5_trajectory_dy = np.zeros((1, 3)) # N x 3 array: position, velocity, acceleration
    polynomial5_trajectory_dz = np.zeros((1, 3)) # N x 3 array: position, velocity, acceleration

    with open(outCSV,mode='w') as csvoutput:
        fieldName = ['id','x','y','z','rx','ry','rz','t']
        csv_writer = csv.writer(csvoutput, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(fieldName)
        for i in range(t_us.shape[0]):
            polynomial5_trajectory_x[0,:], polynomial5_trajectory_y[0,:], polynomial5_trajectory_z[0,:],polynomial5_trajectory_dx[0,:], polynomial5_trajectory_dy[0,:], polynomial5_trajectory_dz[0,:] = polynomial5_interpolation.getPosition(t_us[i])
            if polynomial5_trajectory_x[0,:] is not None:
                csv_writer.writerow([i+1,polynomial5_trajectory_x[0,0],polynomial5_trajectory_y[0,0],polynomial5_trajectory_z[0,0],
                                        polynomial5_trajectory_dx[0,0],polynomial5_trajectory_dy[0,0],polynomial5_trajectory_dz[0,0],t_us[i]])

    # #%% ************************ Linear interpolation *******************************
    # linear_interpolation = LinearInterpolation('Linear', q_given, t_given)
    # linear_trajectory = np.zeros((t.shape[0], 3)) # N x 3 array: position, velocity, acceleration

    # for i in range(t.shape[0]):
    #     linear_trajectory[i,:] = linear_interpolation.getPosition(t[i])

    # plt.figure(figsize=(8, 6))
    # plt.subplot(3,1,1)
    # plt.plot(t_given, q_given[:, 0], 'ro')
    # plt.plot(t, linear_trajectory[:,0], 'k')
    # plt.grid('on')
    # plt.title('Linear interpolation')
    # plt.xlabel('time')
    # plt.ylabel('position')
    # plt.xlim(t_given[0]-1, t_given[-1]+1)
    # plt.ylim(min(q_given[:,0]) - 1, max(q_given[:,0]) + 1)

    # plt.subplot(3,1,2)
    # plt.plot(t_given, q_given[:, 1], 'ro')
    # plt.plot(t, linear_trajectory[:,1], 'k')
    # plt.grid('on')
    # plt.xlabel('time')
    # plt.ylabel('velocity')
    # plt.xlim(t_given[0]-1, t_given[-1]+1)

    # plt.subplot(3,1,3)
    # plt.plot(t_given, q_given[:, 2], 'ro')
    # plt.plot(t, linear_trajectory[:,2], 'k')
    # plt.grid('on')
    # plt.xlabel('time')
    # plt.ylabel('acceleration')
    # plt.xlim(t_given[0]-1, t_given[-1]+1)


    # #%% ************************ Parabolic interpolation *******************************
    # parabolic_interpolation = ParabolicInterpolation('Parabolic', q_given, t_given)
    # parabolic_trajectory = np.zeros((t.shape[0], 3)) # N x 3 array: position, velocity, acceleration

    # for i in range(t.shape[0]):
    #     parabolic_trajectory[i,:] = parabolic_interpolation.getPosition(t[i])

    # plt.figure(figsize=(8, 6))
    # plt.subplot(3,1,1)
    # plt.plot(t_given, q_given[:, 0], 'ro')
    # plt.plot(t, parabolic_trajectory[:,0], 'k')
    # plt.grid('on')
    # plt.title('Parabolic interpolation')
    # plt.xlabel('time')
    # plt.ylabel('position')
    # plt.xlim(t_given[0]-1, t_given[-1]+1)
    # plt.ylim(min(q_given[:,0]) - 1, max(q_given[:,0]) + 1)

    # plt.subplot(3,1,2)
    # plt.plot(t_given, q_given[:, 1], 'ro')
    # plt.plot(t, parabolic_trajectory[:,1], 'k')
    # plt.grid('on')
    # plt.xlabel('time')
    # plt.ylabel('velocity')
    # plt.xlim(t_given[0]-1, t_given[-1]+1)

    # plt.subplot(3,1,3)
    # plt.plot(t_given, q_given[:, 2], 'ro')
    # plt.plot(t, parabolic_trajectory[:,2], 'k')
    # plt.grid('on')
    # plt.xlabel('time')
    # plt.ylabel('acceleration')
    # plt.xlim(t_given[0]-1, t_given[-1]+1)


    # #%% ************************ Cubic interpolation *******************************
    # cubic_interpolation = CubicInterpolation('Cubic', q_given, t_given)
    # cubic_trajectory = np.zeros((t.shape[0], 3)) # N x 3 array: position, velocity, acceleration

    # for i in range(t.shape[0]):
    #     cubic_trajectory[i,:] = cubic_interpolation.getPosition(t[i])

    # plt.figure(figsize=(8, 6))
    # plt.subplot(3,1,1)
    # plt.plot(t_given, q_given[:, 0], 'ro')
    # plt.plot(t, cubic_trajectory[:,0], 'k')
    # plt.grid('on')
    # plt.title('Cubic interpolation')
    # plt.xlabel('time')
    # plt.ylabel('position')
    # plt.xlim(t_given[0]-1, t_given[-1]+1)
    # plt.ylim(min(q_given[:,0]) - 1, max(q_given[:,0]) + 1)

    # plt.subplot(3,1,2)
    # plt.plot(t_given, q_given[:, 1], 'ro')
    # plt.plot(t, cubic_trajectory[:,1], 'k')
    # plt.grid('on')
    # plt.xlabel('time')
    # plt.ylabel('velocity')
    # plt.xlim(t_given[0]-1, t_given[-1]+1)

    # plt.subplot(3,1,3)
    # plt.plot(t_given, q_given[:, 2], 'ro')
    # plt.plot(t, cubic_trajectory[:,2], 'k')
    # plt.grid('on')
    # plt.xlabel('time')
    # plt.ylabel('acceleration')
    # plt.xlim(t_given[0]-1, t_given[-1]+1)


    #%% *************** Polynomial of degree five interpolation *********************
    polynomial5_interpolation = Polynomial5Interpolation('Polynomial5', x_given,  y_given, z_given,  dx_given,  dy_given, dz_given, t_given)
    polynomial5_trajectory_x = np.zeros((t.shape[0], 3)) # N x 3 array: position, velocity, acceleration
    polynomial5_trajectory_y = np.zeros((t.shape[0], 3)) # N x 3 array: position, velocity, acceleration
    polynomial5_trajectory_z = np.zeros((t.shape[0], 3)) # N x 3 array: position, velocity, acceleration
    polynomial5_trajectory_dx = np.zeros((t.shape[0], 3)) # N x 3 array: position, velocity, acceleration
    polynomial5_trajectory_dy = np.zeros((t.shape[0], 3)) # N x 3 array: position, velocity, acceleration
    polynomial5_trajectory_dz = np.zeros((t.shape[0], 3)) # N x 3 array: position, velocity, acceleration

    for i in range(t.shape[0]):
        polynomial5_trajectory_x[i,:], polynomial5_trajectory_y[i,:], polynomial5_trajectory_z[i,:],polynomial5_trajectory_dx[i,:], polynomial5_trajectory_dy[i,:], polynomial5_trajectory_dz[i,:] = polynomial5_interpolation.getPosition(t[i])

    plt.figure(figsize=(8, 6))
    ####################################################
    plt.subplot(18,1,1)
    plt.plot(t_given, x_given[:, 0], 'ro')
    plt.plot(t, polynomial5_trajectory_x[:,0], 'k')
    plt.grid('on')
    plt.title('Polynomial of degree 5 interpolation')
    plt.xlabel('time')
    plt.ylabel('position')
    plt.xlim(t_given[0]-1, t_given[-1]+1)
    plt.ylim(min(x_given[:,0]) - 1, max(x_given[:,0]) + 1)

    plt.subplot(18,1,2)
    plt.plot(t_given, x_given[:, 1], 'ro')
    plt.plot(t, polynomial5_trajectory_x[:,1], 'k')
    plt.grid('on')
    plt.xlabel('time')
    plt.ylabel('velocity')
    plt.xlim(t_given[0]-1, t_given[-1]+1)

    plt.subplot(18,1,3)
    plt.plot(t_given, x_given[:, 2], 'ro')
    plt.plot(t, polynomial5_trajectory_x[:,2], 'k')
    plt.grid('on')
    plt.xlabel('time')
    plt.ylabel('acceleration')
    plt.xlim(t_given[0]-1, t_given[-1]+1)
    #######################################################
    plt.subplot(18,1,4)
    plt.plot(t_given, y_given[:, 0], 'ro')
    plt.plot(t, polynomial5_trajectory_y[:,0], 'k')
    plt.grid('on')
    plt.title('Polynomial of degree 5 interpolation')
    plt.xlabel('time')
    plt.ylabel('position')
    plt.xlim(t_given[0]-1, t_given[-1]+1)
    plt.ylim(min(y_given[:,0]) - 1, max(y_given[:,0]) + 1)

    plt.subplot(18,1,5)
    plt.plot(t_given, y_given[:, 1], 'ro')
    plt.plot(t, polynomial5_trajectory_y[:,1], 'k')
    plt.grid('on')
    plt.xlabel('time')
    plt.ylabel('velocity')
    plt.xlim(t_given[0]-1, t_given[-1]+1)

    plt.subplot(18,1,6)
    plt.plot(t_given, y_given[:, 2], 'ro')
    plt.plot(t, polynomial5_trajectory_y[:,2], 'k')
    plt.grid('on')
    plt.xlabel('time')
    plt.ylabel('acceleration')
    plt.xlim(t_given[0]-1, t_given[-1]+1)
    #######################################################
    plt.subplot(18,1,7)
    plt.plot(t_given, z_given[:, 0], 'ro')
    plt.plot(t, polynomial5_trajectory_z[:,0], 'k')
    plt.grid('on')
    plt.title('Polynomial of degree 5 interpolation')
    plt.xlabel('time')
    plt.ylabel('position')
    plt.xlim(t_given[0]-1, t_given[-1]+1)
    plt.ylim(min(z_given[:,0]) - 1, max(z_given[:,0]) + 1)

    plt.subplot(18,1,8)
    plt.plot(t_given, z_given[:, 1], 'ro')
    plt.plot(t, polynomial5_trajectory_z[:,1], 'k')
    plt.grid('on')
    plt.xlabel('time')
    plt.ylabel('velocity')
    plt.xlim(t_given[0]-1, t_given[-1]+1)

    plt.subplot(18,1,9)
    plt.plot(t_given, z_given[:, 2], 'ro')
    plt.plot(t, polynomial5_trajectory_z[:,2], 'k')
    plt.grid('on')
    plt.xlabel('time')
    plt.ylabel('acceleration')
    plt.xlim(t_given[0]-1, t_given[-1]+1)
    #######################################################
    plt.subplot(18,1,10)
    plt.plot(t_given, dx_given[:, 0], 'ro')
    plt.plot(t, polynomial5_trajectory_dx[:,0], 'k')
    plt.grid('on')
    plt.title('Polynomial of degree 5 interpolation')
    plt.xlabel('time')
    plt.ylabel('position')
    plt.xlim(t_given[0]-1, t_given[-1]+1)
    plt.ylim(min(dx_given[:,0]) - 1, max(dx_given[:,0]) + 1)

    plt.subplot(18,1,11)
    plt.plot(t_given, dx_given[:, 1], 'ro')
    plt.plot(t, polynomial5_trajectory_dx[:,1], 'k')
    plt.grid('on')
    plt.xlabel('time')
    plt.ylabel('velocity')
    plt.xlim(t_given[0]-1, t_given[-1]+1)

    plt.subplot(18,1,12)
    plt.plot(t_given, dx_given[:, 2], 'ro')
    plt.plot(t, polynomial5_trajectory_dx[:,2], 'k')
    plt.grid('on')
    plt.xlabel('time')
    plt.ylabel('acceleration')
    plt.xlim(t_given[0]-1, t_given[-1]+1)
    #######################################################
    plt.subplot(18,1,13)
    plt.plot(t_given, dy_given[:, 0], 'ro')
    plt.plot(t, polynomial5_trajectory_dy[:,0], 'k')
    plt.grid('on')
    plt.title('Polynomial of degree 5 interpolation')
    plt.xlabel('time')
    plt.ylabel('position')
    plt.xlim(t_given[0]-1, t_given[-1]+1)
    plt.ylim(min(dy_given[:,0]) - 1, max(dy_given[:,0]) + 1)

    plt.subplot(18,1,14)
    plt.plot(t_given, dy_given[:, 1], 'ro')
    plt.plot(t, polynomial5_trajectory_dy[:,1], 'k')
    plt.grid('on')
    plt.xlabel('time')
    plt.ylabel('velocity')
    plt.xlim(t_given[0]-1, t_given[-1]+1)

    plt.subplot(18,1,15)
    plt.plot(t_given, dy_given[:, 2], 'ro')
    plt.plot(t, polynomial5_trajectory_dy[:,2], 'k')
    plt.grid('on')
    plt.xlabel('time')
    plt.ylabel('acceleration')
    plt.xlim(t_given[0]-1, t_given[-1]+1)
    #######################################################
    plt.subplot(18,1,16)
    plt.plot(t_given, dz_given[:, 0], 'ro')
    plt.plot(t, polynomial5_trajectory_dz[:,0], 'k')
    plt.grid('on')
    plt.title('Polynomial of degree 5 interpolation')
    plt.xlabel('time')
    plt.ylabel('position')
    plt.xlim(t_given[0]-1, t_given[-1]+1)
    plt.ylim(min(dz_given[:,0]) - 1, max(dz_given[:,0]) + 1)

    plt.subplot(18,1,17)
    plt.plot(t_given, dz_given[:, 1], 'ro')
    plt.plot(t, polynomial5_trajectory_dz[:,1], 'k')
    plt.grid('on')
    plt.xlabel('time')
    plt.ylabel('velocity')
    plt.xlim(t_given[0]-1, t_given[-1]+1)

    plt.subplot(18,1,18)
    plt.plot(t_given, dz_given[:, 2], 'ro')
    plt.plot(t, polynomial5_trajectory_dz[:,2], 'k')
    plt.grid('on')
    plt.xlabel('time')
    plt.ylabel('acceleration')
    plt.xlim(t_given[0]-1, t_given[-1]+1)
    #######################################################
    # #%% ************************** Comparison ***************************
    # plt.figure(figsize=(8, 6))
    # plt.subplot(3,1,1)
    # plt.plot(t_given, q_given[:, 0], 'ro', label='given pos')
    # plt.plot(t, linear_trajectory[:,0], 'k', label='linear')
    # plt.plot(t, parabolic_trajectory[:,0], 'b', label='parabolic')
    # plt.plot(t, cubic_trajectory[:,0], 'g', label='cubic')
    # plt.plot(t, polynomial5_trajectory[:,0], 'm', label='poly 5')
    # plt.grid('on')
    # plt.legend(loc='upper right')
    # plt.title('Comparison')
    # plt.xlabel('time')
    # plt.ylabel('position')
    # plt.xlim(t_given[0]-1, t_given[-1]+3)
    # plt.ylim(min(q_given[:,0]) - 1, max(q_given[:,0]) + 1)

    # plt.subplot(3,1,2)
    # plt.plot(t_given, q_given[:, 1], 'ro', label='given vel')
    # plt.plot(t, linear_trajectory[:,1], 'k', label='linear')
    # plt.plot(t, parabolic_trajectory[:,1], 'b', label='parabolic')
    # plt.plot(t, cubic_trajectory[:,1], 'g', label='cubic')
    # plt.plot(t, polynomial5_trajectory[:,1], 'm', label='poly 5')
    # plt.grid('on')
    # plt.legend(loc='upper right')
    # plt.xlabel('time')
    # plt.ylabel('velocity')
    # plt.xlim(t_given[0]-1, t_given[-1]+3)

    # plt.subplot(3,1,3)
    # plt.plot(t_given, q_given[:, 2], 'ro', label='given acc')
    # plt.plot(t, linear_trajectory[:,2], 'k', label='linear')
    # plt.plot(t, parabolic_trajectory[:,2], 'b', label='parabolic')
    # plt.plot(t, cubic_trajectory[:,2], 'g', label='cubic')
    # plt.plot(t, polynomial5_trajectory[:,2], 'm', label='poly 5')
    # plt.grid('on')
    # plt.legend(loc='upper right')
    # plt.xlabel('time')
    # plt.ylabel('acceleration')
    # plt.xlim(t_given[0]-1, t_given[-1]+3)


    plt.show()