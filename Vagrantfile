# -*- mode: django -*-
# vi: set ft=python :

# Module to know the host platform
# Based on BernardoSilva's answer in http://stackoverflow.com/questions/26811089/vagrant-how-to-have-host-platform-specific-provisioning-steps
module OS
    def OS.mac?
        (/darwin/ =~ RUBY_PLATFORM) != nil
    end
    def OS.linux?
      not OS.mac?
    end
end

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = '2'

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "generic/debian11"
  config.vm.box_check_update = true
  config.vm.define "RexChain"

  # Open ports:
  # 5432 - Postgres
  # 8000 - Django
  [5432, 8000].each do |p|
    config.vm.network :forwarded_port, guest: p, host: p
  end

  # NFS ---- NFS improves speed of VM if supported by your OS
  config.vm.provision :shell, inline: 'apt-get update; apt-get -y install nfs-common portmap', run: "always"
  # It does not work with encrypted volumes
  # Linux Need a plugin for Virtualbox to shared files `vagrant plugin install vagrant-vbguest`
  if OS.linux?
    puts "Vagrant launched from linux."
    config.vm.synced_folder '.', '/vagrant', type: 'virtualbox'
  elsif OS.mac?
    puts "Vagrant launched from mac."
    config.vm.network 'private_network', ip: '192.168.56.10'
    config.vm.synced_folder '.', '/vagrant',
      type: "nfs",
      nfs_version: 3,
      nfs_udp: false
  end

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  config.vm.provider 'virtualbox' do |vb|
    vb.customize ['modifyvm', :id, '--memory', '1024']
  end

  # Provision application
  config.vm.provision "shell", privileged: false, run: "always", path: "config/vagrantvars"
  config.vm.provision "shell", privileged: false, run: "always", path: "bin/install_redis.sh"
  config.vm.provision "shell", privileged: false, run: "always", path: "bin/setup_box.sh"

end
