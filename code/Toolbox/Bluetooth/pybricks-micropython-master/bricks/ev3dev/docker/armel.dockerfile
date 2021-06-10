FROM ev3dev/debian-stretch-cross
RUN sudo apt-get update && \
    DEBIAN_FRONTEND=noninteractive sudo apt-get install --yes --no-install-recommends \
        alsa-utils \
        build-essential \
        espeak \
        ev3dev-media \
        ev3dev-mocks \
        git \
        libasound2-plugin-ev3dev \
        libasound2-plugin-ev3dev:armel \
        libasound2:armel \
        libc6-dbg:armel \
        libffi-dev:armel \
        libglib2.0-0-dbg:armel \
        libgrx-3.0-2-dbgsym:armel \
        libgrx-3.0-dev:armel \
        libi2c-dev \
        libudev-dev:armel \
        libumockdev0:armel \
        pkg-config \
        python \
        python3 \
        uthash-dev:armel \
        xfonts-100dpi
RUN apt-get download umockdev:armel && \
    ar x umockdev*.deb data.tar.xz && \
    sudo tar -C / -xf data.tar.xz ./usr/lib/arm-linux-gnueabi/libumockdev-preload.so.0.0.0 && \
    sudo tar -C / -xf data.tar.xz ./usr/lib/arm-linux-gnueabi/libumockdev-preload.so.0 && \
    rm data.tar.xz && rm *.deb
# Hack to get correct linux/i2c-dev.h header file in cross compiler
# Kernel version of i2c-dev.h is in /usr/arm-linux-gnueabi/include/ which is first in search path
# thanks https://stackoverflow.com/a/36287466/1976323
RUN sudo mv /usr/arm-linux-gnueabi/include/linux/i2c-dev.h /usr/arm-linux-gnueabi/include/linux/i2c-dev.h.kernel && \
    sudo cp /usr/include/linux/i2c-dev.h /usr/arm-linux-gnueabi/include/linux/i2c-dev.h
RUN sudo rm /etc/fonts/conf.d/70-no-bitmaps.conf
ENV PKG_CONFIG_PATH=/usr/lib/arm-linux-gnueabi/pkgconfig
ENV CROSS_COMPILE=arm-linux-gnueabi-
ENV BUILD=build-armel
ENV PYBRICKS_BUILD_ENV=docker-armel
