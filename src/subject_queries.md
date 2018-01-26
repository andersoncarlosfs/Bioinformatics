## 1. Genes with same official first name in ncbi and unit prot but with different secondary names

Admitting they share NO secondary names

	SELECT n.gene_id, d.protein_id
	FROM ncbi n, description_unitprot d
	WHERE d.category = 'recname'
	-- conditions for having the same official first name
	AND (n.symbol = d.name OR d.name = n.full_name_from_nomenclature_authority)
	--
	AND not exists 
	(
		SELECT ni.gene_id, di.protein_id
		FROM ncbi ni, description_unitprot di
		WHERE n.gene_id = ni.gene_id
		AND d.protein_id = di.protein_id
		-- conditions for having the
		-- same secondary name
		-- Write here !
		--
	)

## 2. Genes with same official first name in ncbi and unit prot but with different GO terms

Returns the genes with common GO terms

	SELECT n.gene_id, d.protein_id
	FROM 	ncbi n, 
			description_unitprot d, 
			ncbi_go ngo, 
			go g, 
			go_unitprot gup
			
	WHERE 	n.gene_id = ngo.gene_id
	AND 	ngo.go_id = g.go_id
	AND		g.go_id = gup.go_id

Now for the actual query that answerw the question

	SELECT n.gene_id, d.protein_id
	FROM ncbi ne, description_unitprot de
	WHERE de.category = 'recname'
	-- conditions for having the same official first name
	AND (ne.symbol = de.name OR de.name = ne.full_name_from_nomenclature_authority)
	--
	AND not exists
	(
		SELECT n.gene_id, d.protein_id
		FROM 	ncbi n, 
				description_unitprot d, 
				ncbi_go ngo, 
				go g, 
				go_unitprot gup
				
		WHERE 	n.gene_id = ngo.gene_id
		AND 	ngo.go_id = g.go_id
		AND		g.go_id = gup.go_id
		
		AND n.gene_id = ne.gene_id
		AND d.protein_id = de.protein_id
	)
	
## 3. The distribution of GO terms

I guess it means we want to see the most frequent GO terms, so the ones with the most associations across the database
SQL counters, ugh ...

The simplest thing I can think of, but oh god the perf

It depends on the schema, not sure I understand it
If we admit that 'go' contains every referenced GO term, then it's simple :
	
	SELECT go_id, COUNT(*)
	FROM (
		SELECT g.go_id AS go_id
		FROM go g, ncbi_go ngo
		WHERE g.go_id = ngo.go_id
		UNION
		SELECT g.go_id AS go_id
		FROM go g, go_uniprot upgo
		WHERE g.go_id = upgo.go_id
	)
	GROUP BY go_id

But how do we build go then ? Do we need to do this kind of query beforehand ?

	CREATE TABLE go AS(
		SELECT go_id
		FROM ncbi_go
			UNION
		SELECT go_id
		FROM go_unitprot
	)
otherwise, if there is no table which contains the common go terms between the two datasets :

In fact, I think the one below is just more efficient in either case
But maybe if we want to get the NAMES, then the above might be more efficient

	SELECT go_id, COUNT(*)
	FROM (
		SELECT go_id
		FROM ncbi_go
		UNION go_id
		SELECT go_id
		FROM go_unitprot
	)
	GROUP BY go_id
