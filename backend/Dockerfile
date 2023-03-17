FROM ghcr.io/steamdeckhomebrew/holo-base:latest
RUN pacman -Sydd --noconfirm --dbpath /var/lib/pacman python-pip
RUN pip3 install vdf --target=/vdf
ENTRYPOINT [ "/backend/entrypoint.sh" ]