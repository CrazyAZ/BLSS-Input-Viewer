import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import procon
from threading import Thread, Lock
from collections import deque

FPS = 30
STICK_MAX = 2**15
LEN_QUEUE = 30
DEADZONE_RADIUS = 0.05

def main():
    L = np.zeros(2)
    mutex = Lock()
    
    def get_leftstick(_, l_stick, __, ___, ____, _____):
        l_x, l_y = l_stick
        mutex.acquire()
        try:
            L[0] = l_x / STICK_MAX
            L[1] = l_y / STICK_MAX
        finally:
            mutex.release()
    
    try:
        controller = procon.ProCon()
    except OSError as e:
        print("Could not connect to controller")
        return
    
    t = Thread(target = controller.start, args = (get_leftstick,))
    t.start()

    L_X = deque(np.zeros(LEN_QUEUE))
    L_Y = deque(np.zeros(LEN_QUEUE))

    fig, ax = plt.subplots()
    ln, = plt.plot([], [], color='b')
    dot, = plt.plot([], [], 'o', c='b')
    artists = []

    def init_plot():
        ax.set_aspect('equal')
        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-1.1, 1.1)
        plt.axis('off')

        x_axis, = plt.plot([-1, 1], [0, 0], color='k', alpha=0.5)
        y_axis, = plt.plot([0, 0], [-1, 1], color='k', alpha=0.5)
        artists.append(x_axis)
        artists.append(y_axis)
        deadzone = plt.Circle((0, 0), DEADZONE_RADIUS, color='k', alpha=0.5, linewidth=0)
        ax.add_patch(deadzone)
        artists.append(deadzone)

        circle = plt.Circle((0, 0), 1, color='k', linewidth=5, fill=False)
        ax.add_patch(circle)
        artists.append(circle)

        artists.append(ln)
        artists.append(dot)

        return artists

    def update_plot(_):
        mutex.acquire()
        try:
            l_x, l_y = L
        finally:
            mutex.release()
        
        L_X.popleft()
        L_Y.popleft()
        L_X.append(l_x)
        L_Y.append(l_y)

        if np.linalg.norm([l_x, l_y]) < DEADZONE_RADIUS:
            artists[3].set_color('r')
        else:
            artists[3].set_color('k')

        ln.set_data(L_X, L_Y)
        dot.set_data([l_x], [l_y])
        return artists
        

    ani = FuncAnimation(fig, update_plot, interval=1000.0/FPS, init_func=init_plot, blit=True)
    plt.show()

    controller.stop()
    t.join()

if __name__ == '__main__':
    main()