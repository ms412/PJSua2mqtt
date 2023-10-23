
# -*- Dockerfile -*-

FROM debian:12.2
MAINTAINER Markus Schiesser

RUN apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
            build-essential \
            ca-certificates \
            curl \
            swig \
            wget \
            libgsm1-dev \
            libspeex-dev \
            libspeexdsp-dev \
            libsrtp0-dev \
            libssl-dev \
            portaudio19-dev \
            python3 \
            python3-dev \
            python3-pip \
            python3-virtualenv \
            && \
    apt-get purge -y --auto-remove && rm -rf /var/lib/apt/lists/*

RUN pip install paho-mqtt

COPY config_site.h /tmp/

ENV PJSIP_VERSION=2.13.1
RUN mkdir /usr/src/pjsip && \
    cd /usr/src/pjsip && \
    wget --no-verbose "https://github.com/pjsip/pjproject/archive/refs/tags/$PJSIP_VERSION.tar.gz" -O - | tar zxf -
 #   curl -vsL https://github.com/pjsip/pjproject/archive/refs/tags/${PJSIP_VERSION}.tar.gz | \
  #       tar --strip-components 1 -xf && \

WORKDIR pjproject-$VERSION_PJSIP

#RUN ./configure \
 #     --enable-shared \
  #    --prefix=/install

RUN  ./configure CFLAGS="-fPIC" \
            --enable-shared \
            --disable-opencore-amr \
            --disable-resample \
            --disable-sound \
            --disable-video \
            --with-external-gsm \
            --with-external-pa \
            --with-external-speex \
            --with-external-srtp \
            --prefix=/usr

RUN make dep \
    && make \
    && make install

WORKDIR pjsip-apps/src/swig
RUN make \
    && make install

RUN curl -L