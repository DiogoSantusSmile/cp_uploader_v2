FROM arm64v8/debian:bullseye

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libqt5gui5 \
    libqt5core5a \
    libqt5widgets5 \
    python3-pyqt5 \
    python3-pyqt5.qtsvg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY .. /app

RUN sed -i "/('alembic.ini', '\.')/a \        ('./compile_for_arm_architecture/arm_desktop_shortcut', '.')," main.spec
RUN sed -i '/PyQt5==/d; /PyQt5-Qt5/d; /PyQt5_sip/d' requirements.txt

RUN pip install -r requirements.txt