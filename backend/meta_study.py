import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Example meta-study function

def meta_study_from_matrix(matrix_json, n_clusters=3):
    """
    Given a document matrix (list of dicts), cluster and aggregate findings.
    Returns cluster assignments and top terms per cluster.
    """
    df = pd.DataFrame(matrix_json)
    tfidf = TfidfVectorizer(stop_words='english')
    X = tfidf.fit_transform(df['summary'])
    kmeans = KMeans(n_clusters=min(n_clusters, len(df)), random_state=42).fit(X)
    df['cluster'] = kmeans.labels_
    # Top terms per cluster
    terms = tfidf.get_feature_names_out()
    top_terms = {}
    for i in range(kmeans.n_clusters):
        center = kmeans.cluster_centers_[i]
        top_indices = center.argsort()[-5:][::-1]
        top_terms[i] = [terms[idx] for idx in top_indices]
    # Aggregate
    clusters = df.groupby('cluster')['filename'].apply(list).to_dict()
    return {
        'clusters': clusters,
        'top_terms': top_terms,
        'matrix': df.to_dict(orient='records')
    }

# Example usage
if __name__ == "__main__":
    # Simulate input from API
    matrix = [
        {'filename': 'report1.txt', 'summary': 'AI in healthcare is growing rapidly.', 'entities': 'AI, healthcare'},
        {'filename': 'report2.txt', 'summary': 'Machine learning improves diagnostics.', 'entities': 'machine learning, diagnostics'},
        {'filename': 'report3.txt', 'summary': 'AI and ML are used in medical imaging.', 'entities': 'AI, ML, medical imaging'},
    ]
    result = meta_study_from_matrix(matrix)
    print(result) 