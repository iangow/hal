library(ggplot2)
library(dplyr)

options(stringsAsFactors=FALSE)

words <- read.csv('words.csv')
words$stop_word_type <- c('bio_word'='Bio Word', 'last_name'='Last Name')[words$stop_word_type]

print_graph <- function(block) {
    g <- (
        ggplot(block, aes(x=position, y=stop_word_id)) +
        facet_grid(stop_word_type ~ path, scales='free') +
        geom_point(alpha=0.25) +
        theme_bw() +
        ylab('Stop Word ID') +
        xlab('Sentence Index in Document') +
        ggtitle('Visual Display of Stop Word Locations')
    )
    print(g)
    return(g)
}

pdf(file="words.pdf", paper="USr")
words %>% group_by(path) %>% do(graph=print_graph(.))
dev.off()
