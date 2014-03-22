
#include <stdio.h>

typedef char S1;
typedef short S2;
typedef int S4;
typedef long long S8;

int i = 1000;

int func(int arg)
{
	int test;
	test = 1 ? 2 : 1;
	test = test + 2;
	
	if (test < 5) {
		test += 10;
	}else {
		test -= 10;
	}
	
	switch (test) {
	case 0:
		printf("1");
		break;
	case 1:
		printf("1");
		break;
	case 2:
		printf("1");
		break;
	case 3:
		printf("1");
		break;
	case 4:
		printf("1");
		break;
	default:
		printf("1");
		break;
	}
	
	printf("i = %d\n", i);
	{
		int i = 10;
		printf("i = %d\n", i);
		i += 10;
		i += 20;
		i = (2 == 2);
		printf("i = %d\n", i);
	}
	int i;
	++i;
	printf("i = %d\n", i);
	i = -i;
	i = -i;
	!i;
	i <<= 1;
	i++;
	--i;
	--i;
	i *= 2 * 3;
	i *= 2;
	i += 100;
	i += 1;
	int i2 = i / 2;
	i = i / i2;
	i = i + 1;
	3 - 4;
	printf("i = %d\n", i);
	
	int hoge = 100;
	hoge = 200;
	
	!i;
	
	S1 a = (S2)10;
	a = a - (1000 - 977);
	
	a *= a;
	S1 b = 32;
	a += b;

	b = (1 != 1);
	b = (2 == 2);
	b *= 2 * 4;
	b *= b;
	
	if (a != 0) {
		a += 10;
	}else {
		a *= 10000;
	}
	
	a += b;
	
	S8 c = 1000;
	
	c = a;
}

int main(int argc, char* argv[])
{
	func(10);
}

