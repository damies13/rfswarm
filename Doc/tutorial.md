
# rfswarm tutorial
---

WARNING: This tutorial is a work in progress - it is no where near ready to be used.

---

- [Application Under Test](#Application-Under-Test)
- [Robot Script](#Robot-Script)
- [Run the Test](#Run-the-Test)


For this tutorial you will need at least 1 but ideally 3 or more computers, the roles of these machines are:
- Application Under Test (AUT) - for this we will use open cart
- rfswarm GUI/Server
- rfswarm Agents

## Application Under Test

download opencart virtual machine image
https://bitnami.com/stack/opencart/virtual-machine




```
select p.name, c.name, c1.name from oc_product_description p join oc_product_to_category pc on p.product_id = pc.product_id join oc_category_description c on pc.category_id = c.category_id left join oc_category_path cp on c.category_id = cp.category_id and cp.path_id <> cp.category_id left join oc_category_description c1 on c1.category_id = cp.path_id;

+--------------------------+-------------------------+------------+
| name                     | name                    | name       |
+--------------------------+-------------------------+------------+
| Product 8                | Desktops                | NULL       |
| iPod Classic             | Desktops                | NULL       |
| iPod Classic             | MP3 Players             | NULL       |
| iPhone                   | Desktops                | NULL       |
| iPhone                   | Phones &amp; PDAs       | NULL       |
| HTC Touch HD             | Desktops                | NULL       |
| HTC Touch HD             | Phones &amp; PDAs       | NULL       |
| MacBook Air              | Laptops &amp; Notebooks | NULL       |
| MacBook Air              | Desktops                | NULL       |
| MacBook Pro              | Laptops &amp; Notebooks | NULL       |
| Palm Treo Pro            | Desktops                | NULL       |
| Palm Treo Pro            | Phones &amp; PDAs       | NULL       |
| iPod Nano                | MP3 Players             | NULL       |
| Sony VAIO                | Laptops &amp; Notebooks | NULL       |
| Sony VAIO                | Desktops                | NULL       |
| HP LP3065                | Laptops &amp; Notebooks | NULL       |
| HP LP3065                | Desktops                | NULL       |
| iPod Touch               | MP3 Players             | NULL       |
| iMac                     | Mac                     | Desktops   |
| Samsung SyncMaster 941BW | Desktops                | NULL       |
| Samsung SyncMaster 941BW | Monitors                | Components |
| iPod Shuffle             | MP3 Players             | NULL       |
| MacBook                  | Laptops &amp; Notebooks | NULL       |
| MacBook                  | Desktops                | NULL       |
| Nikon D300               | Cameras                 | NULL       |
| Samsung Galaxy Tab 10.1  | Tablets                 | NULL       |
| Apple Cinema 30&quot;    | Desktops                | NULL       |
| Apple Cinema 30&quot;    | Monitors                | Components |
| Canon EOS 5D             | Desktops                | NULL       |
| Canon EOS 5D             | Cameras                 | NULL       |
+--------------------------+-------------------------+------------+
30 rows in set (0.00 sec)
```


## Robot Script


> While I have some test cases against the opencart demo application, i'm reluctant to provide them until the the rest of this tutorial is Completed as people might load up the demo site without first getting permission from the opencart team to do so. I do not want to encourage people to do this.

## Run the Test



.
