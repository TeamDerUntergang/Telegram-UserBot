# Credits @NaytSeyd
FROM naytseyd/sedenbot:latest

# Maintainer
MAINTAINER Ahmet Acikgoz <NaytSeyd@yandex.com>

# Zaman dilimini ayarla
ENV TZ=Europe/Istanbul

# Çalışma dizini
ENV PATH="/root/sedenuser/bin:$PATH"
WORKDIR /root/sedenuser

# Repoyu klonla
RUN git clone -b seden https://github.com/TeamDerUntergang/Telegram-UserBot /root/sedenuser

# Oturum ve yapılandırmayı kopyala (varsa)
COPY ./sample_config.env ./sedenbot.session* ./config.env* /root/sedenuser/

# Botu çalıştır
CMD ["python3","seden.py"]
