import pathlib
import numpy as np
import loopfit as lf
from simulation import single_pixel
import gdstk
import logging

directory = pathlib.Path(__file__).parent.absolute()

def find_resonance(name, folder ='sonnet/testing', **kwargs):

    # Create single pixel if file does not exist
    file = directory / pathlib.Path(folder) / (name + ".ts")
    if not file.is_file():
        single_pixel(name=name,folder=folder, **kwargs)


    # Load in the data to run the simulation
    f, i, q = lf.load_touchstone(file)
    mag = 10 * np.log10(i**2 + q**2)

    # Re-simulate if Sonnet didn't converge
    index = np.argmin(mag)
    if mag[index] > -10 and index not in [0, mag.size - 1]:
        kwargs['f1'] = round(f[index] / 0.01) * 0.01 - 0.1
        kwargs['f2'] = round(f[index] / 0.01) * 0.01 + 0.1
        kwargs['overwrite'] = True
        single_pixel(name=name,folder=folder, **kwargs)

        # Load in the data.
        f, i, q = lf.load_touchstone(file)
        mag = 10 * np.log10(i**2 + q**2)

        # Raise an error if the simulation still does not look good.
        index = np.argmin(mag)
        if mag[index] > -10 and index not in [0, mag.size - 1]:
            raise RuntimeError(f"'{name}' did not converge.")


def fit(name, folder="sonnet/testing", plot=False):
    file = directory / pathlib.Path(folder) / (name + ".ts")
    f, i, q = lf.load_touchstone(file)
    mag = 10 * np.log10(i ** 2 + q ** 2)
    index = np.argmin(mag)
    mask = (f > f[index] - 0.1) & (f < f[index] + 0.1)
    guess = lf.guess(f[mask], i[mask], q[mask], phase0=0, phase1=0)
    result = lf.fit(f[mask], i[mask], q[mask], **guess)
    if plot:
        from matplotlib import pyplot as plt  # delay pyplot import
        fig, axes = plt.subplots(ncols=2)
        m = lf.model(f[mask], **result)
        axes[0].plot(i[mask], q[mask], 'o', label='data')
        axes[0].plot(m.real, m.imag, label='fit')
        axes[0].set_xlabel("I")
        axes[0].set_ylabel("Q")
        axes[0].axis('equal')
        axes[0].legend()

        axes[1].plot(f[mask], 10 * np.log10(i[mask]**2 + q[mask]**2), 'o')
        axes[1].plot(f[mask], 10 * np.log10(m.real**2 + m.imag**2))
        axes[1].set_xlabel("Frequency [GHz]")
        axes[1].set_ylabel("$S_{21}$ [dB]")
        fig.tight_layout()
        plt.show()
    return result


if __name__ == "__main__":

    logging.basicConfig(level='INFO') # spits information out into the terminal
    library = gdstk.Library()
    # feed = dict(center_width=8, gap=3, height=200, ground2_width=0.5, bottom_ground_height=24, cavity_height=115)
    # ind = dict(spacing_between_inductor_waveguide=7, inductor_width=2, inductor_overlap=7, inductor_length=900)
    cap_low = dict(coupling_bar_height=54.75)
    cap_high = dict(fill=0, coupling_bar_height=0)
    find_resonance("pixel_low", folder="sonnet/testing", epsilon=9.3, capacitor_kwargs=cap_low, f1=4, f2=6)
    find_resonance("pixel_high", folder="sonnet/testing", epsilon=9.3, capacitor_kwargs=cap_high, f1=6, f2=8)
    fit("pixel_low", folder="sonnet/testing", plot=True)
    fit("pixel_high", folder="sonnet/testing", plot=True)
