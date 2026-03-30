# Build AmneziaWG tools and Go implementation
FROM golang:1.22-alpine AS builder

RUN apk add --no-cache git make build-base

# Build awg-go
WORKDIR /build-go
RUN git clone https://github.com/amnezia-vpn/amneziawg-go.git . && make

# Build awg tools
WORKDIR /build-tools
RUN git clone https://github.com/amnezia-vpn/amneziawg-tools.git . && \
    cd src && make

# Create final minimal image
FROM alpine:latest
RUN apk add --no-cache bash iptables iproute2 openresolv

# We copy awg-go and toolset
COPY --from=builder /build-go/amneziawg-go /usr/bin/awg-go
COPY --from=builder /build-tools/src/awg /usr/bin/awg
COPY --from=builder /build-tools/src/awg-quick /usr/bin/awg-quick

# AmneziaWG awg-quick requires the actual backend binary to be known or wg-quick equivalent
# Some users/scripts might expect 'wg' to exist
RUN ln -s /usr/bin/awg /usr/bin/wg && \
    ln -s /usr/bin/awg-quick /usr/bin/wg-quick

ENTRYPOINT ["/bin/bash"]
