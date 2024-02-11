FROM --platform=linux/x86_64 public.ecr.aws/lambda/python:3.11 AS base

RUN yum install -y yum-utils rpmdevtools
WORKDIR /tmp/rpms
RUN yumdownloader --resolve \
    libffi \
    libffi-devel \
    cairo \
    pango \
    glibc
    WORKDIR /tmp/extracted
RUN for rpm in /tmp/rpms/*.rpm; do rpm2cpio "$rpm" | cpio -idmv; done

WORKDIR /opt/lib
RUN cp -P -R /tmp/extracted/usr/lib64/* .
RUN cp -P -R /tmp/extracted/usr/lib/* .
RUN ls -larth && ln libcairo.so.2 libcairo.so && \
    ln libpango-1.0.so.0 pango-1.0 && \
    ln libpangocairo-1.0.so.0 pangocairo-1.0

WORKDIR /opt
RUN pip3 install weasyprint -t python
RUN zip -r /var/task/weasyprint_lambda_layer.zip ./lib ./python
