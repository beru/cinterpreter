
#include <stdio.h>

int g_a;
int g_b;

int hoge2(int arg0)
{
	int test = arg0 + g_a;
	int test2 = 0;
	for (int i=test - 5; i<test; ++i) {
		test2 += i;
	}
	
}

int hoge(int arg0, int arg1)
{
	for (int i=arg0; i<arg1; ++i) {
		hoge2(i);
	}
	
	return 0;
}

int main(int argc, char* argv[])
{
	printf("%p\n", main);
	printf("%d\n", g_a);
	int hoge;
	int main = 0;
	main = 1000;
	printf("%d\n", main);
	for (int i=0; i<5; ++i) {
		if (i == 2) {
			hoge = 10;
		}
	}
	return 0;
	for (int i=0; i<5; ++i) {
		for (int j=0; j<5; ++j) {
			if (i == 3) {
				break;
			}
			{
				continue;
			}
			++i;
		}
		printf("%d\n", i);
	}
	return 0;
}

