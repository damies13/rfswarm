import sys
import os
import os.path
import shutil
import java.lang.System as JS

oslabel = ""
rfswarm_ver = "v0.8.0"

def make_active():
    click("1622358894504.png")
    if has(Pattern("1622430997117.png").similar(0.90)):
        click("1622430997117.png")

def click_new():
    click("1622358928597.png")
    click_index1()

def click_open():
    click("1622359053924.png")

def click_settings():
    click("1622427780268.png")

def click_play():
    click("1622432476336.png")

def click_stop():
    click("1622439564657.png")

def click_abort():
    click("1622439632003.png")

def click_aborted():
    click("1622439752532.png")

def click_Yes():
    click("1622439689474.png")

def click_No():
    click("1622439720128.png")

def click_cancel():
    click("1622429454155.png")

def click_index1():
    click("1622422803344.png")

def click_Agents():
    click(Pattern("1622429245991.png").similar(0.90))

def click_About():
    click(Pattern("1622429261731.png").similar(0.90))

def click_Run():
    click(Pattern("1622432017632.png").similar(0.90))

def click_Plan():
    click(Pattern("1622430997117.png").similar(0.90))


def open_scenario(scenario):
    click_open()

    if has("1622429623038.png", 3):
        click_No()
        waitVanish("1622429623038.png")


    wait("1622359588105.png")
    type("g", Key.META + Key.SHIFT)
    type(scenario)
    type(Key.ENTER)
    # click("1622359900886.png")
    wait(2)
    type(Key.ENTER)
    wait(1)
    click_index1()

def update_oslabel():
    global oslabel
    #print oslabel
    if sys.platform.startswith("java"):
        oslabel = JS.getProperty("os.name") # + JS.getProperty("os.version")

        if JS.getProperty("os.name").startswith("Mac OS"):
            oslabel = "MacOS"

    else:
        oslabel = sys.platform
        #print oslabel
        if oslabel == "darwin":
            oslabel = "MacOS"
        if oslabel == "win32":
            oslabel = "Windows"
        if oslabel == "cygwin":
            oslabel = "Windows"
    #print oslabel


def takess(catagory, name):
    if len(oslabel)<1:
        update_oslabel()
        print oslabel
    wait(5) # give time for graphs and other elements to update
    bounds = getBounds()
    print bounds

    ss = capture(bounds)
    print ss
    nf = "{}_{}_{}_{}.png".format(oslabel, catagory, rfswarm_ver, name)
    print nf
    # print getBundlePath()
    sp = os.path.dirname(getBundlePath())
    print sp
    if not os.path.exists(os.path.join(sp, "screenshots")):
        os.mkdir(os.path.join(sp, "screenshots"))
    nfp = os.path.join(sp, "screenshots", nf)
    print nfp
    # os.path
    shutil.move(ss, nfp)

def gui_ss():

    click_new()
    takess("Plan", "New")

    click_settings()
    takess("Plan", "Test_Settings")
    click_cancel()

    open_scenario("/Users/dave/Documents/GitHub/rfswarm/Scenarios/100u_test.rfs")
    click_settings()
    takess("Plan", "Test_Settings_Filter_Rules")
    click_cancel()

    open_scenario("/Users/dave/Documents/GitHub/rfswarm/Scenarios/150 users stepped in groups of 25.rfs")
    takess("Plan", "150u_25per10min")

    open_scenario("/Users/dave/Documents/GitHub/rfswarm/Scenarios/test2.rfs")
    takess("Plan", "saved_opened")

    open_scenario("/Users/dave/Documents/GitHub/rfswarm/Scenarios/Simple_delay.rfs")
    takess("Plan", "20u_delay_example")

    click_new()

    click_Agents()
    takess("Agents", "Ready")

    click_About()
    takess("About", "About")

def gui_run():

    click_new()

    open_scenario("/Users/dave/Documents/GitHub/rfswarm/Scenarios/30u5r20m.rfs")

    click_Agents()
    wait("1622432336397.png", 300)
    click_Plan()
    click_play()
    wait(5)
    takess("Run", "Start_5s")
    wait(55)
    takess("Run", "Start_60s")

    click_Agents()
    takess("Agents", "Runing")

    click_Run()
    click_stop()
    takess("Run", "Bomb_Run")
    wait(10)
    click_Agents()
    takess("Agents", "Stopping")

    click_Run()
    click_abort()
    takess("Run", "Abort_Dialogue")
    click_Yes()
    click_aborted()
    takess("Run", "Aborted")

def gui_2h():

    click_new()

    open_scenario("/Users/dave/Documents/GitHub/rfswarm/Scenarios/100u_test.rfs")

    click_Agents()
    wait("1622432336397.png", 300)
    

    click_Plan()
    click_play()


make_active()

#gui_ss()

#gui_run()

gui_2h()
