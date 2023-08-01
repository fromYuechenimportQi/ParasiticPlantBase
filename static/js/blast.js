$('document').ready(function () {
    var data = "";
    $.ajaxSetup({
        cache: false
    });
    $.ajax({
        url: document.URL,
        type: "GET",
        success: function (response) {
            data = response;
            for (const i of response) {
                $('#species').append(`<option value=${i.species}>${i.species}</option>`);
            }
            for (const i of data) {
                if (i.species == $('#species').val()) {
                    for (const j of i.information) {
                        $('#databaseOptions').append(`<option value=${j.description}>${j.description}</option>`);
                    }
                }
            }
        },
        error: function (error) {
            console.log(error)
        }
    });
    $("#species").change(function () {
        $("#databaseOptions").empty();
        var selectedSpecies = $('#species').val();
        for (const i of data) {
            if (i.species == selectedSpecies) {
                for (const j of i.information) {
                    $('#databaseOptions').append(`<option value=${j.description}>${j.description}</option>`);
                }
            }
        }
    })
    $("#loading").hide();
    function findAllGt(str) {
        arr = [];
        index = -1;
        do {
            index = str.indexOf(">", index + 1);
            if (index !== -1)
                arr.push(index);
        } while (index !== -1);
        return arr;
    }

    function sliceQueries(str, gtArr) {
        queries = [];
        if (gtArr.length == 1) {
            queries.push(str);
        }
        for (let i = 1; i < gtArr.length; i++) {
            temp = str.slice(gtArr[i - 1], gtArr[i]);
            queries.push(temp);

            if (i == gtArr.length - 1) {
                temp = str.slice(gtArr[i]);
                queries.push(temp);
            }

        }
        return queries;
    }

    function readFasta(queryInput) {
        queryObj = {};
        if (!queryInput) {
            return "";
        }
        else if (queryInput[0] !== ">") {
            queryInput = ">Unkown_query\n" + queryInput;
        }
        queryInput = queryInput.replace(/\n/g, '\\n');
        queries = sliceQueries(queryInput, findAllGt(queryInput));
        for (const query of queries) {
            enterIdx = query.indexOf('\\n');
            seqName = query.slice(0, enterIdx + 2);
            seq = query.slice(enterIdx + 2);
            queryObj[seqName] = seq;
        }
        return queryObj;
    }
    // testStr = "AGACAVAGACAC\nAGACACAC\n>test\nACCAGAF"

    class BlastQuery {
        constructor(fastaObj) {
            this.failed = function () {
                alert("Your query sequence is invalid. Check the sequence please.")
            }
            if (fastaObj instanceof Object == false) {
                this.failed();
            }
            this.fasta = {
                queries: fastaObj,
                dataBase: ""
            };
            this.setDataBase = function (database) {
                this.fasta.dataBase = database;
            }
            this.getQueries = function () {
                console.log(this.fasta);
            }
            this.isDNASequence = function () {
                for (const seqInfo of Object.values(this.fasta.queries)) {
                    if (seqInfo.search(/[^AGCTURYMKSWHBVDN\\n\s]/i) !== -1) {
                        this.failed();
                        return false;
                    }
                }
                return true;

            };
            this.isProtSequence = function () {
                for (const seqInfo of Object.values(this.fasta.queries)) {
                    if (seqInfo.search(/[^AGCTFUDNEQHLIKOMPRSVWYBZJX\\n\s]/i) !== -1) {
                        this.failed();
                        return false;
                    }
                }
                return true;
            }
            this.toJson = function () { }
        }
    }
    $("#submit").click(function () {
        var text = $("textarea").val();
        var query = new BlastQuery(readFasta(text));
        var cmd = $("input[name='blastOptions']:checked").val();
        if (text == "") {
            return false;
        }
        else if (text.length > 20000) {
            return false;
        }
        else if (cmd == 'blastn' || cmd == 'blastx') {
            if (!query.isDNASequence()) {
                return false;
            }
        }
        else if (cmd == 'blastp' || cmd == 'tblastn') {
            if (!query.isProtSequence()) {

                return false;
            }
        }
        $("#loading").show();
        $("#loading").nextAll().css("filter", "brightness(50%)");
        $("#blt").submit();
    });
    $("#example").click(function () {
        var test = `ATGGCCACCCAAGTCCCGCCTCATCCCGGCACTGTCCCTCCGACCGATTCGAATCCGGCGGCCACCCAACCGGAAAAGACGGACTACATGAATCTGCCTTGCCCTATTCCTTATGAAGAAATCCAACGCGAAGCTCTCATGTCATTGAAGCCAGAACTTTTTGAAGGAATGCGCTTTGATTTTACCAAAGCACTAAACCAGAGATTTTCTCTCAGTCACAGCGTATTCATGGGACCCACAGAAGTTCCTTCTCAGTCCACTGAAACAATTAAAATACCAACTGCTCATTATGAGTTTGGTGCAAACTTTATAGACCCACAGATGATGCTTTTTGGGCGGCTGATGACAGATGGGAGGCTAAATGCTAGGCTAAAGTGTGATTTGTCTGAAAATCTTTCTCTGAAAGGAAATGCTCAACTTACATCTGAGCAACACATGTCACATGGGATGGTCAATTTTGATTACAAGGGAAAAGACTACAGGACTCAATTTCAACTTGGCAGTGGTGCATTGCTGGGAGCCAGTTACATCCAGAGTGTTACCCCTCATTTATCGCTGGGCGGTGAAGTATTCTGGGCTGGCCAGCATCGTAAATCTGGCATTGGCTATGTTGGCCGGTACAACACAGACAAGATGGTTGCCGCAGGTCAAGTTGCTAGCACAGGAATAGTTGCACTCAGCTATGTTCAGAAAGTTTCTGAGAAGGTTTCTTTAGCATCAGACTTCATGTACAACTACTTATCAAGAGATGTTACAGCCAGCTTTGGTTATGATTACATTCTTAGACAGTGTCGTCTTAGAGGGAAAATTGATTCCAATGGCTGTATCACTTCTTTCTTAGAAGAGCGGTTGAACATGGGACTTAATTTCATTCTCTCTGCAGAGGTCGATCACAAGAAGAAAGACTATAAGTTTGGGTTTGGGATAACGGTTGGAGAATAA`
        var text = $("textarea").val();
        if (!text) {
            $("textarea").val(test);
        } else {
            $("textarea").val("");
        }

    })
});