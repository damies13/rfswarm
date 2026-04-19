*** Settings ***
Library    checkprime.py

*** Variables ***

*** Tasks ***
My Example Test Case
    [Documentation]    run a test case
	Do Some Things
	# Do Some Fruity Things
	# Do Something

*** Keywords ***
Do Some Things
	Do First Thing
	Do Second Thing
	Do Third Thing

Do Something
	Log 	Do Something
	Sleep 	1
	Get Primes 	max=8

Do First Thing
	Log 	Do First Thing
	# Sleep 	0.3
	Sleep 	1
	Get Primes 	max=10

Do Second Thing
	Log 	Do Second Thing
	# Sleep 	0.3
	Sleep 	2
	Get Primes 	max=20

Do Third Thing
	Log 	Do Third Thing
	# Sleep 	0.3
	Sleep 	3
	Get Primes 	max=30

Do Some Fruity Things
	Do Banana Thing
	Do Mango Thing
	Do Soursop Thing
	Do Guava Thing
	Do Rumbutan Thing
	Do Longan Thing

Do ${Named} Thing
	Log 	Do ${Named} Thing
	Sleep 	0.3 	Sleep for Do ${Named} Thing
	Get Primes 	max=13


Get Primes
	[Arguments] 	${min}=1 	${max}=888
	# [x for x in range(1,100) if is_prime(x)]
	FOR    ${num} 	IN RANGE 	${min} 	${max}
		${isprime}= 	Is Prime 	${num}
		IF 	${isprime}
			# Log 	${num} is a prime number 	console=true
			Log 	${num} is a prime number
		END
	END

 #
