


#include <iostream>
using namespace std;

// базовый уровень
void base()
{
    double side1, side2, side3,perimeter;                 //создал переменные
    cout << "Введи стороны треугольника:" << "\n";        //предложил ввод
    cin >> side1 >> side2 >> side3;                       //ввод
    if (cin.fail() || side1<=0 || side2<=0 || side3<=0)   //проверка ввода
    {
        cout << "Неверный тип данных, введите положительное число" << "\n";
        cin.clear();
        cin.ignore(10000,'\n');
        return;
    }
    perimeter = side1 + side2 + side3;                     //вычисление периметра
    cout << "Периметр треугольника = " << perimeter;       //вывод
}

// средний уровень
void medium()
{
    double length1, length2;                                     //создал переменные
    cout << "Введите длины двух отрезков в сантиметрах" << "\n"; //предложил ввод
    cin >> length1 >> length2;                                   //ввод
    if (cin.fail() || length1 <= 0 || length2 <= 0)              //проверка ввода
    {
        cout << "Неверный тип данных, введите положительное число" << "\n";
        cin.clear();
        cin.ignore(10000, '\n');
        return;
    }
    double sumlength;                                             //переменная суммы длин
    sumlength = length1 + length2;
    double cm;                                                    //переменная сантиметров
    cm = sumlength - ((static_cast<int>(sumlength)/100) * 100);
    cout << "Сумма длин отрезков в метрах = " << (static_cast<int>(sumlength) / 100) << endl << "Сумма длин отрезков в сантиметрах = " << cm << "\n"; //вывод

}

// продвинутый уровень
void hard()
{
    double price;                                               //созздал перменные
    int tip;
    cout << "Введите стоимость обеда и % чаевых" << "\n";       //предложение ввода
    cin >> price >> tip;                                        //ввод
    if (cin.fail() || price <= 0 || tip < 0)                    //проверка ввода
    {
        cout << "Неверный тип данных, введите положительное число" << "\n";
        cin.clear();
        cin.ignore(10000, '\n');
        return;
    }
    double cost{ price + (static_cast<double>(price) / 100) * tip }; //инициализация перменной итогового вывода и ее расчет
    cout << "Общая стоимость = " << cost << endl;                    //вывод
}

int main()
{
    int task_level; //переменная выбора уровня задания
    cout << "Выберите уровень задания:" << "\n" << "1 - базовый" << "\n" << "2 - средний" << "\n" << "3 - продвинутый" << endl; //предложение выбрать уровень задания
    cin >> task_level; //ввод уровня задания
    if (cin.fail()) //проверка ввода
    {
        cout << "Неверный ввод. Введите число";
        cin.clear();
        cin.ignore(10000, '\n');
        return 0;
    }
    if (task_level == 1)
    {
        base();
    }
    else if (task_level == 2)
    {
        medium();
    }
    else if (task_level ==3)
    {
        hard();
    }
    else
    {
        cout << "Ошибка. Нужно ввести 1 или 2 или 3" << endl; //на случай если пользователь вводит не 1/2/3
    }
    return 0;
}

