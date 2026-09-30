# Copyright (C) 2026 ETH Zurich. All rights reserved.
#
# Authors:
#     - Cedric Hirschi, ETH Zurich
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y --no-install-recommends \
    ca-certificates unzip xz-utils git python3 python3-pip python3-protobuf protobuf-compiler usbutils \
    build-essential pkg-config libgl1 libglib2.0-0 libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

# --- Install SLT (copied from build context) ---
# Put the SLT linux zip you downloaded next to this Dockerfile as slt-linux.zip
COPY slt-cli-1.0.1-linux-x64.zip /tmp/slt-linux.zip
RUN mkdir -p /opt/silabs/slt \
    && unzip -q /tmp/slt-linux.zip -d /opt/silabs/slt \
    && rm /tmp/slt-linux.zip

# Make sure slt is found
ENV PATH="/opt/silabs/slt:${PATH}"

# Copy SLT recipe + install packages
# Fresh slt-cli 1.0.1 has no Conan remotes.json; update --self installs it
COPY cli_tools.toml /tmp/cli_tools.toml
RUN slt update --self --non-interactive \
    && slt install -f /tmp/cli_tools.toml --non-interactive

# Add tool paths to path
COPY populate_path.sh /tmp/populate_path.sh
RUN sed -i 's/\r$//' /tmp/populate_path.sh
RUN /bin/bash /tmp/populate_path.sh

# Add Wiseconnect extension
COPY setup_wiseconnect.sh /tmp/setup_wiseconnect.sh
RUN sed -i 's/\r$//' /tmp/setup_wiseconnect.sh
RUN /bin/bash /tmp/setup_wiseconnect.sh

# Set `python` to point to `python3`
RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /work
CMD ["/bin/bash"]
