FROM golang:alpine AS builder

RUN apk add --no-cache git make build-base libmnl-dev linux-headers

# Build awg-go
WORKDIR /build-go
COPY src/awg-go /build-go
RUN make

# Build awg tools
WORKDIR /build-tools
COPY src/awg-tools /build-tools
RUN cd src && make

# Create final minimal image
FROM alpine:latest
RUN apk add --no-cache bash iptables iproute2 openresolv

# We copy awg-go and toolset
COPY --from=builder /build-go/amneziawg-go /usr/bin/awg-go
COPY --from=builder /build-tools/src/wg /usr/bin/awg
COPY --from=builder /build-tools/src/wg-quick/linux.bash /usr/bin/awg-quick

# AmneziaWG awg-quick requires the actual backend binary to be known or wg-quick equivalent
RUN chmod +x /usr/bin/awg-go /usr/bin/awg /usr/bin/awg-quick && \
    ln -s /usr/bin/awg-go /usr/bin/wg-go && \
    ln -s /usr/bin/awg-go /usr/bin/amneziawg-go && \
    ln -s /usr/bin/awg /usr/bin/wg && \
    ln -s /usr/bin/awg-quick /usr/bin/wg-quick

ENTRYPOINT ["/bin/bash"]
