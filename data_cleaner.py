import spacy # For NLP (Natural Language Processing)

def get_human_legible_txt(signal_sources_txt):
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")

    # Time to clean extracted data to something a human can read.
    # Step 1 - VERBS AND NOUNS
    nlp = spacy.load("en_core_web_sm")

    def has_verb_and_noun(sent):
        doc = nlp(sent)
        has_verb = any(t.pos_ == "VERB" for t in doc)
        has_noun = any(t.pos_ in ("NOUN", "PROPN") for t in doc)
        return has_verb and has_noun

    def has_lowercase_word(sent):
        return any(word.islower() for word in sent.split())

    # Step 2 - PUNCTUATION
    import string

    def has_punctuation(sent):
        return any(char in string.punctuation for char in sent)

    # Step 3 - LENGTH
    def long_enough(sent):
        return len(sent.split()) > 6

    # Step 4 - NOT SYMBOL DENSE
    def not_symbol_heavy(sent):
        symbols = sum(not c.isalnum() and not c.isspace() for c in sent)
        return symbols / max(len(sent), 1) < 0.3

    # Calculate Sentence Score
    def is_human_readable(sent):
        return(
            has_verb_and_noun(sent)
            and has_lowercase_word(sent)
            and long_enough(sent)
            and not_symbol_heavy(sent)
            and has_punctuation(sent)
        )

    human_readable_source_txt = []
    for source in signal_sources_txt:
        candidate_sentences = [sent.strip() for sent in source["results"][0]["raw_content"].split("\n") if sent.strip()]

        # Filter
        human_sentences = [s for s in candidate_sentences if is_human_readable(s)]
        human_text = "\n".join(human_sentences)
        human_readable_source_txt.append(human_text)

    return human_readable_source_txt