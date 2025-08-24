#!/usr/bin/env python3
"""
Add gender labels to articles_with_summaries.json based on creator names
"""

import json
import re

def determine_gender(name):
    """
    Determine gender based on first name
    Returns: 'male', 'female', or 'unknown'
    """
    # Extract first name
    first_name = name.split()[0].lower()
    
    # Common male names in the dataset
    male_names = {
        'brandon', 'ben', 'ken', 'marty', 'marc', 'ryan', 'roman', 'clay', 
        'daniel', 'tren', 'stewart', 'stuart', 'sachin', 'richard', 'rich',
        'andrew', 'joseph', 'mohit'
    }
    
    # Common female names in the dataset
    female_names = {
        'teresa', 'melissa', 'julie', 'amy', 'hannah', 'shayna', 'madison',
        'eira', 'swetha', 'merci', 'ishita', 'louron', 'iuliia', 'steffi',
        'alena'
    }
    
    if first_name in male_names:
        return 'male'
    elif first_name in female_names:
        return 'female'
    else:
        # For uncertain cases, return unknown and print for manual review
        print(f"Unknown gender for name: {name} (first name: {first_name})")
        return 'unknown'

def add_gender_labels(input_file, output_file):
    """
    Read JSON file, add gender labels, and save updated version
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        print(f"Processing {len(articles)} articles...")
        
        # Add gender field to each article
        for article in articles:
            creator_name = article.get('creator', '')
            gender = determine_gender(creator_name)
            article['gender'] = gender
            
            print(f"Track {article.get('track_id')}: {creator_name} -> {gender}")
        
        # Save updated JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        
        print(f"\nUpdated JSON saved to: {output_file}")
        
        # Print summary
        gender_counts = {}
        for article in articles:
            gender = article['gender']
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
        
        print("\nGender distribution:")
        for gender, count in gender_counts.items():
            print(f"  {gender}: {count}")
        
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    input_file = "../Content/articles/raw_metadata/articles_with_summaries.json"
    output_file = "../Content/articles/raw_metadata/articles_with_summaries_updated.json"
    
    add_gender_labels(input_file, output_file)