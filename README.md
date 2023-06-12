# biodiversityPathway

This is a FastAPI/Tortoise ORM application designed to create CRUD operations for interacting with deep learning protein embeddings from Meta's ESM model. You can make POST requests to populate the database with your protein information. In this demo, we'll explore proteins related to nicotine biosynthesis.

## Protein Data Acquisition

The following steps outline how to gather and upload protein data:

1. **Visit the UniprotKB Website**
    * Navigate to the [UniprotKB website](https://www.uniprot.org/).

2. **Search for Relevant Proteins**
    * Enter the following search query: `Nicotine AND (taxonomy_id:4085)`
        * This query retrieves proteins related to nicotine from the plant Nicotiana family.

3. **Export Search Results**
    * Extract the search results into a JSON file.

4. **Upload Data**
    * Use the `uniprotkb.ipynb` notebook to upload the extracted data.

5. **BLAST the Proteins**
    * Use BLAST to obtain the primary accessions of the proteins from the UniprotKB JSON.

6. **Upload BLAST Results**
    * Use the `blast_results.ipynb` notebook to upload the BLAST results.

This process yields approximately 200 proteins from the initial UniprotKB search and around 2000 proteins from the BLASTing process.

## Generating Deep Learning Embeddings and UMAP Components

Next, we'll utilize Meta's ESM model to gather deep learning embeddings and UMAP components:

* **Run ESM**
    * Use the `run_esm.ipynb` notebook to collect the deep learning embeddings.

* **Get UMAP Components**
    * Use the `get_components.ipynb` notebook to generate the UMAP components.

These procedures will gather all the necessary data and upload it to a PostgreSQL database. This data can then be utilized by a frontend application to visualize the results.
