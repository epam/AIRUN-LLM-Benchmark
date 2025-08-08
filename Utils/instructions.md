# SDLC Benchmark Development Instructions

## Основная задача

Разработка бенчмарка для тестирования способности LLM следовать инструкциям при инкрементальной разработке React компонентов. Цель - найти слабые места моделей при выполнении последовательных инструкций по доработке кода.

## Концепция бенчмарка

### Принцип работы
1. **Initial Prompt** → LLM генерирует React компонент → **Iteration 1**
2. **Initial Prompt + Iteration 1 + Step 2** → LLM дорабатывает компонент → **Iteration 2**
3. **Initial Prompt + Iteration 1 + Step 2 + Iteration 2 + Step 3** → **Iteration 3**
4. И так далее (планируем 2-3 итерации)

### Ключевые принципы
- **Инкрементальность**: Каждая итерация ДОРАБАТЫВАЕТ предыдущую, а не переписывает с нуля
- **Накопительное тестирование**: На iteration N должны проходить тесты iteration_1.test.tsx, iteration_2.test.tsx, ..., iteration_N.test.tsx
- **Обратная совместимость**: Новые функции не должны ломать существующие

## Структура проекта

```
Utils/
├── sdlc_experiment.py              # Основные промпты для бенчмарка
├── task1.py                        # Экспериментальная площадка для новых промптов
├── task3.py                        # Counter компонент с props (4 итерации)
├── task4.py                        # Todo list компонент с props (4 итерации)
├── sdlc_js_test_runner.py          # Запуск тестов и сбор результатов
├── enhanced_counter_component/     # Результаты генерации counter компонента
│   ├── step_1/component.tsx        # Базовый counter
│   ├── step_2/component.tsx        # Reset + custom step
│   ├── step_3/component.tsx        # Validation + bounds
│   └── step_4/component.tsx        # Persistence + history
├── enhanced_todo_component/        # Результаты генерации todo компонента
│   ├── step_1/component.tsx        # Базовый todo list
│   ├── step_2/component.tsx        # Delete + validation
│   ├── step_3/component.tsx        # Filters + search
│   └── step_4/component.tsx        # Persistence + bulk actions
└── sdlc_test/                      # Тестовая среда
    ├── package.json                # Jest конфигурация с виртуальными моками
    └── src/
        ├── setupTests.tsx          # Глобальные моки для отсутствующих библиотек
        ├── counter_component/      # Тесты для counter компонента
        │   ├── component.tsx       # Копия компонента от LLM для тестирования
        │   ├── iteration_1.test.tsx # Тесты базового функционала (98 tests)
        │   ├── iteration_2.test.tsx # Тесты reset + step (134 tests)
        │   ├── iteration_3.test.tsx # Тесты validation + bounds (162 tests)
        │   └── iteration_4.test.tsx # Тесты persistence + history (233 tests)
        └── todo_component/         # Тесты для todo компонента
            ├── iteration_1.test.tsx # Тесты базового функционала (115 tests)
            ├── iteration_2.test.tsx # Тесты delete + validation (142 tests)
            ├── iteration_3.test.tsx # Тесты filters + search (179 tests)
            └── iteration_4.test.tsx # Тесты persistence + bulk (203 tests)
```

## Процесс разработки бенчмарка

### 1. Создание промптов (task1.py)
- Разрабатываем последовательность инструкций
- Тестируем на разных моделях
- Анализируем получаемые компоненты

### 2. Написание тестов
- На основе промптов создаем соответствующие iteration_N.test.tsx
- Каждый тест проверяет выполнение конкретных требований
- Тесты должны быть устойчивы к разным стилям кода

### 3. Запуск бенчмарка
- Модель генерирует компонент по промпту
- Компонент сохраняется как component.tsx
- Запускаются ВСЕ тесты до текущей итерации
- Собираются метрики прохождения

## Техническое решение

### Проблема зависимостей
LLM могут использовать любые библиотеки (react-spinners, axios, lodash), которые не установлены.

### Решение - виртуальные моки
```typescript
// setupTests.tsx
jest.mock('react-spinners/ClipLoader', () => {
  return function MockClipLoader(props: any) {
    return <div data-testid="mock-cliploader" {...props}>Spinner</div>;
  };
}, { virtual: true });
```

### Преимущества
- Тесты работают с любыми зависимостями
- Нет необходимости устанавливать библиотеки
- Фокус на логике, а не на UI деталях

## Метрики бенчмарка

### Что измеряем
- **Соблюдение требований**: Проходят ли тесты текущей итерации
- **Обратная совместимость**: Проходят ли тесты предыдущих итераций  
- **Деградация качества**: На какой итерации начинают ломаться старые тесты
- **Понимание контекста**: Насколько хорошо модель учитывает предыдущий код

### Ожидаемые результаты
- Выявление слабых мест LLM в следовании инструкциям
- Понимание, на каких типах задач модели чаще ошибаются
- Данные для улучшения промптинга

## Реализованные компоненты

### Counter Component (task3.py)
4 итерации развития React счетчика с пропсами:
1. **Iteration 1**: Базовый counter с increment/decrement
2. **Iteration 2**: Reset функциональность + custom step
3. **Iteration 3**: Validation + bounds (minValue/maxValue)
4. **Iteration 4**: Persistence в localStorage + history

**Результаты тестирования на GPT-4**: 100% → 97% → 73% → 72% (прогрессивная деградация)

### Todo List Component (task4.py)
4 итерации развития React todo списка с пропсами:
1. **Iteration 1**: Базовый todo list с добавлением
2. **Iteration 2**: Delete функциональность + enhanced validation
3. **Iteration 3**: Фильтры (all/active/completed) + поиск
4. **Iteration 4**: LocalStorage persistence + bulk operations

**Особенности тестов**:
- Props-based testing для максимальной гибкости
- data-testid атрибуты для стабильного доступа к элементам
- Обратная совместимость тестируется на каждой итерации
- localStorage и window.confirm моки для изоляции тестов

## Быстрый старт для нового ассистента

### 1. Понимание контекста
```
Это SDLC бенчмарк для тестирования LLM способности следовать инкрементальным инструкциям при разработке React компонентов. 

Основная цель: найти слабые места моделей при выполнении последовательных инструкций по доработке кода.
```

### 2. Текущее состояние
- ✅ 2 компонента полностью готовы (counter + todo)
- ✅ 8 полных test суites написаны
- ✅ Структура проекта настроена
- ✅ Props-based testing подход внедрен

### 3. Возможные задачи
1. **Запуск тестов**: Анализ результатов существующих компонентов
2. **Новые компоненты**: Создание task5.py для других типов компонентов
3. **Анализ деградации**: Изучение паттернов ошибок в итерациях
4. **Улучшение промптов**: Оптимизация инструкций на основе результатов

### 4. Важные принципы
- **Инкрементальность**: Каждая итерация дорабатывает, не переписывает
- **Props-based testing**: Тесты через пропсы, не хардкод
- **Обратная совместимость**: Новые функции не ломают старые
- **data-testid strategy**: Стабильные селекторы для тестов

## Команды

```bash
cd Utils/sdlc_test
npm test                    # Запуск всех тестов
npm run test:watch         # Разработка в реальном времени
python ../sdlc_js_test_runner.py  # Запуск через Python скрипт

# Генерация новых компонентов
python task3.py             # Запуск counter benchmark
python task4.py             # Запуск todo benchmark
```