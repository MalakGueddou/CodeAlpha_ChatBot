// NLP utilities for text processing
class NLPProcessor {
    constructor() {
        this.stopWords = new Set([
            'le', 'la', 'les', 'de', 'des', 'du', 'et', 'est', 'elle', 'il', 'je', 'tu', 'nous', 'vous', 'ils', 'elles',
            'à', 'au', 'aux', 'avec', 'ce', 'cet', 'cette', 'ces', 'dans', 'pour', 'par', 'sur', 'sous', 'vers', 'chez',
            'mais', 'ou', 'où', 'donc', 'car', 'que', 'qui', 'quoi', 'quand', 'comment', 'pourquoi', 'si', 'comme',
            'est-ce', 'qu\'est-ce', 'quel', 'quelle', 'quels', 'quelles', 'un', 'une', 'des', 'mon', 'ton', 'son', 'notre',
            'votre', 'leur', 'mes', 'tes', 'ses', 'nos', 'vos', 'leurs', 'ceci', 'cela', 'ça', 'celui', 'celle', 'ceux',
            'celles', 'aucun', 'aucune', 'certains', 'certaines', 'tout', 'tous', 'toute', 'toutes', 'plus', 'moins',
            'très', 'trop', 'peu', 'assez', 'aussi', 'alors', 'ensuite', 'puis', 'finalement', 'ainsi', 'donc', 'or', 'ni',
            'ne', 'pas', 'non', 'oui', 'ok', 'd\'accord', 'bonjour', 'salut', 'merci', 'svp', 's\'il vous plaît', 'a', 'as',
            'ai', 'avons', 'avez', 'ont', 'suis', 'es', 'sommes', 'êtes', 'sont', 'étais', 'était', 'étions', 'étiez',
            'étaient', 'serai', 'seras', 'sera', 'serons', 'serez', 'seront', 'sois', 'soit', 'soyons', 'soyez', 'soient',
            'fus', 'fut', 'fûmes', 'fûtes', 'furent', 'sois', 'soit', 'soyons', 'soyez', 'soient', 'ayant', 'eu', 'eue',
            'eus', 'eues', 'eûmes', 'eûtes', 'eurent', 'aie', 'aies', 'ait', 'ayons', 'ayez', 'aient'
        ]);
    }

    // Tokenize and clean text
    preprocessText(text) {
        return text
            .toLowerCase()
            .normalize('NFD').replace(/[\u0300-\u036f]/g, '') // Remove accents
            .replace(/[^\w\s]/g, ' ') // Replace punctuation with spaces
            .replace(/\s+/g, ' ') // Normalize whitespace
            .trim()
            .split(' ')
            .filter(word => word.length > 2 && !this.stopWords.has(word));
    }

    // Calculate term frequency
    calculateTF(tokens) {
        const tf = {};
        tokens.forEach(token => {
            tf[token] = (tf[token] || 0) + 1;
        });
        return tf;
    }

    // Calculate cosine similarity between two texts
    cosineSimilarity(text1, text2) {
        const tokens1 = this.preprocessText(text1);
        const tokens2 = this.preprocessText(text2);
        
        if (tokens1.length === 0 || tokens2.length === 0) return 0;

        const allTokens = [...new Set([...tokens1, ...tokens2])];
        const tf1 = this.calculateTF(tokens1);
        const tf2 = this.calculateTF(tokens2);

        let dotProduct = 0;
        let magnitude1 = 0;
        let magnitude2 = 0;

        allTokens.forEach(token => {
            const val1 = tf1[token] || 0;
            const val2 = tf2[token] || 0;
            dotProduct += val1 * val2;
            magnitude1 += val1 * val1;
            magnitude2 += val2 * val2;
        });

        magnitude1 = Math.sqrt(magnitude1);
        magnitude2 = Math.sqrt(magnitude2);

        if (magnitude1 === 0 || magnitude2 === 0) return 0;

        return dotProduct / (magnitude1 * magnitude2);
    }

    // Find best match using multiple strategies
    findBestMatch(userQuestion, faqs) {
        let bestMatch = null;
        let highestScore = 0;

        // Strategy 1: Direct cosine similarity with question
        faqs.forEach(faq => {
            const similarity = this.cosineSimilarity(userQuestion, faq.question);
            if (similarity > highestScore) {
                highestScore = similarity;
                bestMatch = faq;
            }
        });

        // Strategy 2: Keyword matching for low similarity cases
        if (highestScore < 0.3) {
            const userTokens = this.preprocessText(userQuestion);
            let keywordScore = 0;
            
            faqs.forEach(faq => {
                const faqKeywords = faq.keywords || [];
                const matches = userTokens.filter(token => 
                    faqKeywords.some(keyword => 
                        keyword.includes(token) || token.includes(keyword)
                    )
                ).length;
                
                const currentScore = matches / Math.max(userTokens.length, faqKeywords.length);
                
                if (currentScore > keywordScore) {
                    keywordScore = currentScore;
                    bestMatch = faq;
                }
            });

            highestScore = Math.max(highestScore, keywordScore);
        }

        return {
            faq: bestMatch,
            confidence: highestScore
        };
    }
}