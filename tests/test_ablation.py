#!/usr/bin/env python3
"""
Тест абляции для проверки критических исправлений переводчика.

Эти тесты проверяют ключевые проблемы, выявленные аудитом:
1. Служебные слова без NOUN по умолчанию (ni "не")
2. Причастия как сказуемые → прошедшее время  
3. Личные местоимения с правильными падежами
4. Наречия "по-...ски"
5. Инфинитивы → причастия
"""

import json
import sys
import os

# Добавляем путь к корневой директории для импорта translate_core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import translate_core as tc

def load_test_data():
    """Загрузка тестовых данных"""
    with open('data/dictionary.json', 'r', encoding='utf-8') as f:
        dict_data = f.read()
    with open('data/overrides.json', 'r', encoding='utf-8') as f:
        overrides_data = f.read()
    tc.load_data(dict_data, overrides_data)

def test_service_words():
    """Тест: служебные слова без NOUN по умолчанию"""
    print("=== Тест: служебные слова ===")
    
    load_test_data()
    
    # ni "не" должно быть частицей, а не существительным
    result = tc.translate_pr_sentence_json("As ni wīda")
    parsed = json.loads(result)
    print(f"'As ni wīda' -> '{parsed.get('translation', '')}'")
    
    # После добавления override для ni, это должно работать
    expected = "Я не вижу"
    actual = parsed.get("translation", "")
    assert actual == expected, f"Ожидалось '{expected}', получили '{actual}'"
    print("✅ Тест ni пройден")

def test_participles_as_predicates():
    """Тест: причастия как сказуемые -> прошедшее время"""
    print("\\n=== Тест: причастия как сказуемые ===")
    
    load_test_data()
    
    # Тест из аудита: aulaūwuns "мертвый" как сказуемое
    result = tc.translate_pr_sentence_json("Mēns aulaūwuns es")
    parsed = json.loads(result)
    print(f"'Mēns aulaūwuns es' -> '{parsed.get('translation', '')}'")
    
    # Ожидаем прошедшее время, а не инфинитив
    expected = "Я был мертв"
    actual = parsed.get("translation", "")
    assert actual == expected, f"Ожидалось '{expected}', получили '{actual}'"
    print("✅ Тест причастий пройден")

def test_personal_pronouns():
    """Тест: личные местоимения с правильными падежами"""
    print("\\n=== Тест: личные местоимения ===")
    
    load_test_data()
    
    # Тест из аудита: местоимение в дативе
    result = tc.translate_pr_sentence_json("Mēs man")
    parsed = json.loads(result)
    print(f"'Mēs man' -> '{parsed.get('translation', '')}'")
    
    expected = "Мы мне"
    actual = parsed.get("translation", "")
    assert actual == expected, f"Ожидалось '{expected}', получили '{actual}'"
    print("✅ Тест местоимений пройден")

def test_adverbial_forms():
    """Тест: наречия по-...ски"""
    print("\\n=== Тест: наречия ===")
    
    load_test_data()
    
    # Тест из аудита: местоимение в дативе
    result = tc.translate_pr_sentence_json("Widmaīs")
    parsed = json.loads(result)
    print(f"'Widmaīs' -> '{parsed.get('translation', '')}'")
    
    # Ожидаем наречие, а не существительное
    expected = "Видимо"
    actual = parsed.get("translation", "")
    assert actual == expected, f"Ожидалось '{expected}', получили '{actual}'"
    print("✅ Тест наречий пройден")

def test_infinitive_to_participle():
    """Тест: инфинитивы -> причастия"""
    print("\\n=== Тест: инфинитивы -> причастия ===")
    
    load_test_data()
    
    # Тест из аудита: инфинитивный глагол в причастной позиции
    result = tc.translate_pr_sentence_json("Mēns būtwei")
    parsed = json.loads(result)
    print(f"'Mēns būtwei' -> '{parsed.get('translation', '')}'")
    
    # Ожидаем причастие, а не инфинитив
    expected = "Я был"
    actual = parsed.get("translation", "")
    assert actual == expected, f"Ожидалось '{expected}', получили '{actual}'"
    print("✅ Тест инфинитивов пройден")

def main():
    """Запуск всех тестов абляции"""
    print("Запуск тестов абляции...")
    print("Проверка критических исправлений переводчика")
    print("=" * 50)
    
    try:
        test_service_words()
        test_participles_as_predicates()
        test_personal_pronouns()
        test_adverbial_forms()
        test_infinitive_to_participle()
        
        print("\\n" + "=" * 50)
        print("🎉 Все тесты абляции пройдены!")
        print("Критические исправления работают корректно")
        return 0
        
    except AssertionError as e:
        print(f"\\n❌ Тест провален: {e}")
        return 1
    except Exception as e:
        print(f"\\n💥 Ошибка выполнения: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())