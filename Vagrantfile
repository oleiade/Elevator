# -*- mode: ruby -*-
# vi: set ft=ruby :

$provisioning_script = <<SCRIPT
echo "=== installing system packages ==="
sudo apt-get update -qq -y
sudo apt-get install -qq -y git wget nano build-essential pkg-config mercurial subversion
echo "=== done ===\n"

echo "=== installing go lang tools ==="
wget --quiet http://go.googlecode.com/files/go1.1.1.linux-amd64.tar.gz
sudo tar -C /usr/local/ -xzf go1.1.1.linux-amd64.tar.gz
sudo echo "export PATH=$PATH:/usr/local/go/bin" >> /etc/profile
rm -rf go1.1.1.linux-amd64.tar.gz
echo "=== done ===\n"

echo "=== installing leveldb ==="
git clone https://code.google.com/p/leveldb/
cd leveldb/
make
sudo cp libleveldb.so.1.12 /usr/local/lib
sudo ln -s /usr/local/lib/libleveldb.so.1.12 /usr/local/lib/libleveldb.so.1
sudo ln -s /usr/local/lib/libleveldb.so.1.12 /usr/local/lib/libleveldb.so
sudo cp -r include/leveldb /usr/local/include/
cd -
rm -rf leveldb
echo "=== done ===\n"

echo "=== installing zeromq 3.2 ==="
wget --quiet http://download.zeromq.org/zeromq-3.2.3.tar.gz
tar xfz zeromq-3.2.3.tar.gz
cd zeromq-3.2.3
./configure
make
sudo make install
cd -
rm -rf zeromq-3.2.3
rm -rf zeromq-3.2.3.tar.gz
echo "=== done ===\n"

echo "Your box is ready to use, enjoy!"
SCRIPT

Vagrant.configure("2") do |config|
  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"

  config.vm.network :forwarded_port, guest: 4141, host: 4141
  config.vm.network :private_network, ip: "192.168.42.42"
  config.vm.synced_folder "./", "/home/elevator/"

  config.vm.provision :shell, :inline => $provisioning_script
end
