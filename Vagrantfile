# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"

  config.vm.provider "virtualbox" do |v|
    v.name = "code-challenge"
    v.memory = 1024
    v.cpus = 2
  end

  config.vm.network "forwarded_port", guest: 5000, host: 5000
  config.vm.network "forwarded_port", guest: 443, host: 8443

  config.vm.provision "bootstrap",
    type: "shell",
    inline: <<-SHELL
      sudo apt-get install software-properties-common
      sudo apt-add-repository ppa:ansible/ansible
      sudo apt-get update
      sudo apt-get install ansible
      sudo apt-get autoremove -yq
      sudo ansible-playbook -i "localhost," -c local /opt/code-challenge/repo/playbook.yml
    SHELL

#  config.vm.provision "ansible" do |ansible|
#    ansible.verbose = "v"
#    ansible.playbook = "playbook.yml"
#  end

  config.vm.synced_folder ".", "/opt/code-challenge/repo"
  config.vm.synced_folder "../code-challenge-content", "/opt/code-challenge/content"

end
