
CREATE TABLE public.uniprot (
                protein_id VARCHAR NOT NULL,
                CONSTRAINT uniprot_pk PRIMARY KEY (protein_id)
);
COMMENT ON TABLE public.uniprot IS 'description: 
origins: UniProt
files: UniProt/uniprot-cancer+AND+reviewed%3Ayes+AND+organism%3A%22Homo+sapiens+%28Human%29+%5B--.txt.gz
links: https://web.expasy.org/docs/userman.html';


CREATE TABLE public.description (
                protein_id VARCHAR NOT NULL,
                category VARCHAR NOT NULL,
                type VARCHAR NOT NULL,
                description VARCHAR NOT NULL,
                CONSTRAINT description_pk PRIMARY KEY (protein_id)
);
COMMENT ON TABLE public.description IS 'description: 
origins: UniProt
files: UniProt/uniprot-cancer+AND+reviewed%3Ayes+AND+organism%3A%22Homo+sapiens+%28Human%29+%5B--.txt.gz
links: https://web.expasy.org/docs/userman.html';


CREATE TABLE public.accession_number (
                protein_id VARCHAR NOT NULL,
                accession_number VARCHAR NOT NULL,
                CONSTRAINT accession_number_pk PRIMARY KEY (protein_id, accession_number)
);
COMMENT ON TABLE public.accession_number IS 'description: 
origins: UniProt
files: UniProt/uniprot-cancer+AND+reviewed%3Ayes+AND+organism%3A%22Homo+sapiens+%28Human%29+%5B--.txt.gz
links: https://web.expasy.org/docs/userman.html#AC_line';


CREATE TABLE public.go (
                go_id VARCHAR NOT NULL,
                category VARCHAR NOT NULL,
                CONSTRAINT go_pk PRIMARY KEY (go_id)
);
COMMENT ON TABLE public.go IS 'description:
origins: NCBI
origins: Gene Ontology (GO)
files: gene2go
links:';


CREATE TABLE public.go_uniprot (
                go_id VARCHAR NOT NULL,
                protein_id VARCHAR NOT NULL,
                CONSTRAINT go_uniprot_pk PRIMARY KEY (go_id, protein_id)
);
COMMENT ON TABLE public.go_uniprot IS 'description: 
origins: Gene Ontology (GO)
origins: UniProt
files: UniProt/uniprot-cancer+AND+reviewed%3Ayes+AND+organism%3A%22Homo+sapiens+%28Human%29+%5B--.txt.gz
files: gene2go
links:';


CREATE TABLE public.go_term (
                go_id VARCHAR NOT NULL,
                go_term VARCHAR NOT NULL,
                CONSTRAINT go_term_pk PRIMARY KEY (go_id)
);
COMMENT ON TABLE public.go_term IS 'description:
origins: NCBI
origins: Gene Ontology (GO)
files: gene2go
links:';


CREATE TABLE public.evidence (
                go_id VARCHAR NOT NULL,
                evidence VARCHAR NOT NULL,
                qualifier VARCHAR NOT NULL,
                CONSTRAINT evidence_pk PRIMARY KEY (go_id, evidence, qualifier)
);
COMMENT ON TABLE public.evidence IS 'description: This relation contains information about any evidence
origins: NCBI
origins: Gene Ontology (GO)
files: gene2go
links:';


CREATE TABLE public.ncbi (
                gene_id INTEGER NOT NULL,
                taxonomy_id INTEGER NOT NULL,
                symbol VARCHAR NOT NULL,
                description VARCHAR NOT NULL,
                type_of_gene VARCHAR NOT NULL,
                symbol_from_nomenclature_authority VARCHAR NOT NULL,
                full_name_from_nomenclature_authority VARCHAR NOT NULL,
                nomenclature_status VARCHAR NOT NULL,
                modification_date DATE NOT NULL,
                CONSTRAINT ncbi_pk PRIMARY KEY (gene_id)
);
COMMENT ON TABLE public.ncbi IS 'description: This relation contains information about any gene
origins: NCBI
files: Homo_sapiens.gene_info
files: gene2go
links: https://clin-table-search.lhc.nlm.nih.gov/apidoc/ncbi_genes/v3/doc.html';


CREATE TABLE public.ncbi_go (
                gene_id INTEGER NOT NULL,
                go_id VARCHAR NOT NULL,
                CONSTRAINT ncbi_go_pk PRIMARY KEY (gene_id, go_id)
);
COMMENT ON TABLE public.ncbi_go IS 'description:
origins: NCBI
origins: Gene Ontology (GO)
files: gene2go
links:';


CREATE TABLE public.map_location (
                gene_id INTEGER NOT NULL,
                map_location VARCHAR NOT NULL,
                CONSTRAINT map_location_pk PRIMARY KEY (gene_id, map_location)
);
COMMENT ON TABLE public.map_location IS 'description:
origins: NCBI
files: Homo_sapiens.gene_info
links:';


CREATE TABLE public.feature_type (
                gene_id INTEGER NOT NULL,
                feature_type VARCHAR NOT NULL,
                CONSTRAINT feature_type_pk PRIMARY KEY (gene_id, feature_type)
);
COMMENT ON TABLE public.feature_type IS 'description:
origins: NCBI
files: Homo_sapiens.gene_info
links:';


CREATE TABLE public.other_designation (
                gene_id INTEGER NOT NULL,
                other_designation VARCHAR NOT NULL,
                CONSTRAINT other_designation_pk PRIMARY KEY (gene_id, other_designation)
);
COMMENT ON TABLE public.other_designation IS 'description:
origins: NCBI
files: Homo_sapiens.gene_info
links:';


CREATE TABLE public.chromosome (
                gene_id INTEGER NOT NULL,
                chromosome VARCHAR NOT NULL,
                CONSTRAINT chromosome_pk PRIMARY KEY (gene_id, chromosome)
);
COMMENT ON TABLE public.chromosome IS 'description:
origins: NCBI
files: Homo_sapiens.gene_info
links:';


CREATE TABLE public.db_xref (
                gene_id INTEGER NOT NULL,
                db_xref VARCHAR NOT NULL,
                CONSTRAINT db_xref_pk PRIMARY KEY (gene_id, db_xref)
);
COMMENT ON TABLE public.db_xref IS 'description:
origins: NCBI
files: Homo_sapiens.gene_info
links: https://www.ncbi.nlm.nih.gov/genbank/collab/db_xref/';


CREATE TABLE public.synonym (
                gene_id INTEGER NOT NULL,
                synonym VARCHAR NOT NULL,
                CONSTRAINT synonym_pk PRIMARY KEY (gene_id, synonym)
);
COMMENT ON TABLE public.synonym IS 'description:
origins: NCBI
files: Homo_sapiens.gene_info
links:';


CREATE TABLE public.locus_tag (
                gene_id INTEGER NOT NULL,
                locus_tag VARCHAR NOT NULL,
                CONSTRAINT locus_tag_pk PRIMARY KEY (gene_id, locus_tag)
);
COMMENT ON TABLE public.locus_tag IS 'description:
origins: NCBI
files: Homo_sapiens.gene_info
links: https://www.wikidata.org/wiki/Property:P2393
links: https://www.ncbi.nlm.nih.gov/genbank/eukaryotic_genome_submission_annotation/#locus_tag
links: https://www.ncbi.nlm.nih.gov/genbank/genomesubmit_annotation/#locus_tag';


ALTER TABLE public.accession_number ADD CONSTRAINT uniprot_accession_number_fk
FOREIGN KEY (protein_id)
REFERENCES public.uniprot (protein_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.go_uniprot ADD CONSTRAINT uniprot_go_uniprot_fk
FOREIGN KEY (protein_id)
REFERENCES public.uniprot (protein_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.description ADD CONSTRAINT uniprot_name_fk
FOREIGN KEY (protein_id)
REFERENCES public.uniprot (protein_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.evidence ADD CONSTRAINT ontology_evidence_fk
FOREIGN KEY (go_id)
REFERENCES public.go (go_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.go_term ADD CONSTRAINT gene_ontology_go_term_fk
FOREIGN KEY (go_id)
REFERENCES public.go (go_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.ncbi_go ADD CONSTRAINT gene_ontology_ncbi_go_fk
FOREIGN KEY (go_id)
REFERENCES public.go (go_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.go_uniprot ADD CONSTRAINT go_go_uniprot_fk
FOREIGN KEY (go_id)
REFERENCES public.go (go_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.locus_tag ADD CONSTRAINT gene_locus_tags_fk
FOREIGN KEY (gene_id)
REFERENCES public.ncbi (gene_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.synonym ADD CONSTRAINT gene_synonyms_fk
FOREIGN KEY (gene_id)
REFERENCES public.ncbi (gene_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.db_xref ADD CONSTRAINT gene_db_xref_fk
FOREIGN KEY (gene_id)
REFERENCES public.ncbi (gene_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.chromosome ADD CONSTRAINT gene_chromosome_fk
FOREIGN KEY (gene_id)
REFERENCES public.ncbi (gene_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.other_designation ADD CONSTRAINT gene_other_designation_fk
FOREIGN KEY (gene_id)
REFERENCES public.ncbi (gene_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.feature_type ADD CONSTRAINT gene_feature_type_fk
FOREIGN KEY (gene_id)
REFERENCES public.ncbi (gene_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.map_location ADD CONSTRAINT gene_map_location_fk
FOREIGN KEY (gene_id)
REFERENCES public.ncbi (gene_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.ncbi_go ADD CONSTRAINT ncbi_ncbi_go_fk
FOREIGN KEY (gene_id)
REFERENCES public.ncbi (gene_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;
