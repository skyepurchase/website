---
title: The Birth of Odysseus
date: 24-10-2025
---

# The Birth of Odysseus

At 10:53 on 24th October 2025 `odysseus` came into this world after much blood, sweat, and tears. No warranty was broken but almost certainly some terms and conditions were violated. Much like its namesake it was a long and arduous journey which left me a changed person.

For those of you who are confused this is my laptop finally running Arch (a Linux distribution, you probably already knew that I don't know why I told you[^1]). Though to many installing Arch (or Linux for that matter) may seem like an odyssey in itself (it really isn't) this is not my first rodeo; the OS is not to blame.

_WARNING:_ If you've thought of installing Linux on a machine but are scared, don't read this, this is not a normal instal process.

_DISCLAIMER:_ Don't mess around with a machine you don't own or have a way of returning to an untouched state. This was pretty rash and I was lucky I managed to get it working.

## Set and Setting

I recently started a PhD at Imperial as part of the mathematical department. Doing machine learning/scientific computing meant that I got a "free"[^2] laptop! But there are a few catches:

* It can only be either a HP or a Mac.

Not a problem, I can install Linux on a fresh HP.

* It is a managed machine with HP Wolf Security.

Ah ... that is a problem, no USB booting for me. But the silver lining is that I can get Imperial to install Linux, a inhouse Ubuntu build in particular. I don't want Ubuntu[^4] I want _MY_ Linux setup (which just happens to be Arch for reasons outside of pros and cons of Arch, though there are many pros). But I have Linux, I have root, and _I have grub_. I can now boot from USB!

## In terms of USB we have no USB

Secure boot prevents grub from seeing USB devices so that's a no. But I still have grub, I have internet access and I can access the filesystem. Time to bootstrap and boot from the harddrive itself.

Essentially you

* Drop into the grub commandline (press `c` during the grub menu, which can be enable by editting your grub config).
* Change the root to the partition that contains the iso image, `set root=(hd0,gpt3)` in my case.
* Create a loopback device to treat the iso as a filesystem, `loopback loop $isofile` where `$isofile` is the path to the iso file.
* Run the `linux` and `initrd` commands, `linux (loop)/arch/boot/x86_64/vmlinux img_dev=UUID=$imgdevuuid img_loop=$isofile` and `initrd (loop)/arch/boot/x86_64/initramfs-linux.img`.
* Finally `boot`.

Then it chugs along locating the isofile and initialising the system to drop into a live Arch environment.

## Now You See Me Now You Don't

The system uses Logical Virtual Memory (LVM) so as far as I'm concerned I can't access my filesystem during grub. I can run all the commands above but when it actually boots it can't find the device that stores my iso because it's virtual; grub just sees a random partition with no discernable file system.

I guess we give up this is becoming ridiculous.[^3]
But wait ... the boot partition is not virtual and _incredibly large_, it's 2GB and the current boot files only use 300MB, I can squeeze the iso onto this and no more LVM problems!

## I Used the Stones to Install the Stones

I can boot into the archiso, it's all loaded into RAM and life is good.
There are some minor problems such as some certificates used for the LVM and how that's loaded, I'm not sure but tbh idc atm imma format them.

Everything is set up all I have to do is `pacstrap` and I did it: I circumvented all the security measures.

But pride comes before a fall and the drive will not allow me to write to it. Why? I didn't find out; I was panicked and raged. I had formatted everything so there was no restart. Either I figured this out or I had a very expensive brick.

... I didn't figure it out, I stopped, I had a dinner to get to. I had tried my best but in the end I didn't get my Linux.

I turn on the laptop and it fials. There's no boot files, I still can't access the boot menu, it's a brick.

## Submissive and Bootable

I consider the fact that secure boot with find anything to boot to recover from this catastrophe. So I plug in the USB and power on ... Lo and behold it boots into the archiso!!

This is it! I haven't had to take the SSD out and void warrany, I've got archiso running on a live USB, and full access to the drive. I run through the setup, I create users, sort things out, and reboot.

## In Every "We're So Back" There's a Little "It's Over"

I'm done. I'm in. I have Arch and everything works ... if only. I had forgotten to `pacstrap` `base-devel` or explicitly include `networkmanager`.[^5] I cannot access WiFi and so I cannot download the pacakges to access said WiFi. Once again this system decides to block me out with Catch 22 Logic (tbf this one is actually on me).

## Lost in the Sauce

I originally thought I would need to do the cursed bootstrapping from the beginning (a part of me wanted to so that I could prove I was capable). Then maybe that I would need to wipe the disk again to get a USB boot (but honestly that terrified me). But a [vision from god](https://ellie.clifford.lol) made me realise I can install packages offline.

The first part is reformatting my single USB (I should get more). This was a faff as I originally tried FAT32 but needed more packages and then later realised I needed ext4 because of filename formats. But got there in the end, the real struggle was just beginning.

You can download pacman (Arch _pac_kage _man_ager) packages into a folder rather than installing them with `pacman -Syw --cachedir="$PWD" --dbpath /tmp/blankdb <package>` (the `dbpath` is to get all the dependencies regardless of those installed on the device). this did _not_ work in my home directory for some reason, but it did in `\mnt` and then I could copy all the files to `$HOME/.../packages`. This took hours to figure out and I initially hand transferred files from online sources. This is the main reason I got lost in the sauce.

Once downloaded you can create an offline repo with `repo-add`. Transfer that database back onto the USB mount that onto the faulty system and use `pacman` again. I realise I did it a cursed way and changed the configuration file to ignore all source except the database and ran `-Syu` flags when I could have just used `-U`, oh well.

Anyway, the frustrating journey I took was

* I started with `iw` as it has very few dependencies, easily to hand transfer. But this has no WPA support.
* I then used `iwd` as this was also small and had `iwctl` which is used in the archiso. But some kernel flags or something were wrong.
* I then used `wpa_supplicant` as this was suggested in Arch. This would run and find my SSID but would not connect for inexplicable reasons.
* Finally I used `networkmanager` a very chunky dependency package but I had worked out `-Syw` and so it was less of a pain. It worked, so seemlessly, so much so that I was almost more mad than when I was failing with the previous attempts.

But I am now far more familiar with Linux and Arch than I had ever hoped or wanted to be.

## I'm In

After this I was able to install `i3` get some basic config and set up Firefox. After some tinkering with a better dotfiles/config files setup so that I can share configuration across my devices `odysseus` is self sufficient. The last few bits of configuration I did without my current PC as a lifeline.

Again, I want to reiterate, this is in no way normal for a Linux installation, especially not for incredibly user friendly distros like Ubuntu or Raspbian. Also _I DO NOT ADVICE CIRCUMVENTING COMPANY SECURITY MEASURES_, there's definitely more security that Imperial could have put on the machine but equally I had physical access to the machine. I have a full disk image backup of the Ubuntu build they had that I can put back on if necessary. I did this because I was not going to spend 4 years on the awful build they used, and I wanted to see if I could do it.

[^1]: I do actually know why my mum will read this and ask what Arch is.
[^2]: It's still Imperial's and they will in theory take it back in 4 years time.
[^4]: The straw that broke my back was seemingly being unable to change my keyboard layout for some odd reason.
[^3]: At this point I had sunk 2 days into the research and testing and it still was not working.
[^5]: I had originally thought I just needed `iw` but as you'll see soon this was quite an involved process. `networkmanager` is such a great program and recommend it entirely.
