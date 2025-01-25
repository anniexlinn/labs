"""
6.101 Lab 0:
Audio Processing
"""

import wave
import struct
# No Additional Imports Allowed!


def backwards(sound):
    """
    Reverses the order of a sound's samples
    """
    new = sound.copy()
    backwards_s = new.get("samples").copy()
    backwards_s.reverse()
    new["samples"] = backwards_s
    return new

def mix(sound1, sound2, p):
    """
    Mix 2 sounds according to the mixing parameter p.

    If 2 sounds have different sampling rates, return None
    Length of resulting sound is max of input sound lengths, 
    where the resulting sound is p times samples in sound 1 
    and 1-p times samples in sound 2.

    Returns python dictionary of new mixed sound.
    
    """
    if sound1.get("rate") != sound2.get("rate"):
        return None

    rate = sound1["rate"]
    sound1 = sound1["samples"]
    sound2 = sound2["samples"]
    maximum = max(len(sound1), len(sound2))
    mixed = []
    i = 0
    while i < maximum:
        s1 = sound1[i] * p if i < len(sound1) else 0
        s2 = sound2[i] * (1 - p) if i < len(sound2) else 0
        mixed.append(s1 + s2)
        i += 1
    return {"rate": rate, "samples": mixed}

def convolve(sound, kernel):
    """
    Convolves the sound using the given kernel(filter)
    by shifting and scaling the original sample and 
    combining resulting sequences into the output sound.
    
    """
    samples = []  # initialize scaled sample lists

    for i, sample in enumerate(kernel):
        scaled = [0] * i  # offset scaled sound by filter index
        scaled += [sample * s for s in sound["samples"]]
        samples.append(scaled)

    # combine samples into one list
    final_length = len(sound["samples"]) + len(kernel) - 1
    final = [0] * final_length
    for sample in samples:
        for i, val in enumerate(sample):
            final[i] += val
    return {"rate": sound["rate"], "samples": final}

def echo(sound, num_echoes, delay, scale):
    """
    Apply echo effect to given sound by adding one 
    or more additional copies to the sound, each delayed
    and scaled down to corresponding amounts.
    
    """
    sample_delay = round(delay * sound["rate"])
    echo_filter_length = (sample_delay * num_echoes) + len(sound["samples"])
    # initialize echo filter with zeros
    echo_filter = [0] * echo_filter_length

    # copy original sound samples to echo_filter
    for i in range(len(sound["samples"])):
        echo_filter[i] = sound["samples"][i]

    # add delayed and scaled copies to echo_filter
    for i in range(1, num_echoes + 1):
        offset = i * sample_delay
        # iterate through original sound's samples
        for j in range(len(sound["samples"])):
            # prevent out of bounds indexing
            if j + offset < echo_filter_length:
                echo_filter[j + offset] += scale**i * sound["samples"][j]

    return {"rate": sound["rate"], "samples": echo_filter}

def pan(sound):
    """
    Adjust sounds for left and right channels to achieve a panned
    effect.
    """
    # calculate scaling for left and right sounds
    left_scale = [1 - i / (len(sound["left"]) - 1) for i in range(len(sound["left"]))]
    right_scale = [i / (len(sound["right"]) - 1) for i in range(len(sound["right"]))]

    # apply scaling to left and right channels
    left_channel = [left_scale[i] * sound["left"][i] for i in range(len(left_scale))]
    right_channel = [right_scale[i] * sound["right"][i]
                    for i in range(len(right_scale))]

    return {"rate": sound["rate"], "left": left_channel, "right": right_channel}


def remove_vocals(sound):
    """
    Create mono output sound from stereo input sound.
    """
    # subtract right from left sound to compute stereo
    mono = [sound["left"][i] - sound["right"][i] for i in range(len(sound["left"]))]
    return {"rate": sound["rate"], "samples": mono}

def bass_boost_kernel(n_val, scale=0):
    """
    Construct a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ n_val

    Then we scale that piece up and add a copy of the original signal back in.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    kernel = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    for i in range(n_val):
        kernel = convolve(kernel, base["samples"])
    kernel = kernel["samples"]

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel) // 2] += 1

    return kernel


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds


def load_wav(filename, stereo=False):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    file = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = file.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    if stereo:
        left = []
        right = []
        for i in range(count):
            frame = file.readframes(1)
            if chan == 2:
                left.append(struct.unpack("<h", frame[:2])[0])
                right.append(struct.unpack("<h", frame[2:])[0])
            else:
                datum = struct.unpack("<h", frame)[0]
                left.append(datum)
                right.append(datum)

        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = []
        for i in range(count):
            frame = file.readframes(1)
            if chan == 2:
                left = struct.unpack("<h", frame[:2])[0]
                right = struct.unpack("<h", frame[2:])[0]
                samples.append((left + right) / 2)
            else:
                datum = struct.unpack("<h", frame)[0]
                samples.append(datum)

        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for left, right in zip(sound["left"], sound["right"]):
            left = int(max(-1, min(1, left)) * (2**15 - 1))
            right = int(max(-1, min(1, right)) * (2**15 - 1))
            out.append(left)
            out.append(right)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)

    synth = load_wav("sounds/synth.wav")
    water = load_wav("sounds/water.wav")
    write_wav(mix(synth, water, 0.2), "synth_water_mix.wav")
    # ice_and_chilli = load_wav("sounds/ice_and_chilli.wav")
    # write_wav(convolve(ice_and_chilli, bass_boost_kernel(1000, 1.5)),
    # "ice_and_chilli_convolve.wav")
    # car = load_wav("sounds/car.wav")
    # write_wav(pan(car), "car_pan.wav")
    # lookout_mountain = load_wav("sounds/lookout_mountain.wav")
    # write_wav(remove_vocals(lookout_mountain), "lookout_mountain.wav")
