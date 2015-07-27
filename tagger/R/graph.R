library(ggplot2)
library(dplyr)

options(stringsAsFactors=FALSE)

lines <- read.csv('../output/lines.csv')
lines$folder <- gsub('-', '/', gsub('[^-0-9]', '', lines$path))

bio_region <- function(block) {
    bio_lines <- block$line[block$bio == 1]
    ribbon <- data.frame(
        x=c(min(bio_lines), max(bio_lines)),
        ymin=0,
        ymax=1,
        Region='actual'
        )
}
actual_regions <- lines %>% group_by(folder) %>% do(bio_region(.))

predictions <- read.csv('../output/predictions.csv')
bio_region <- function(block) {
    ribbon <- data.frame(
        x=c(block$start, block$stop),
        ymin=0,
        ymax=1,
        Region='predicted'
        )
}
predicted_regions <- predictions %>% group_by(folder) %>% do(bio_region(.))
regions <- bind_rows(actual_regions, predicted_regions)

print_graph <- function(folder) {
    g <- (
        ggplot(lines[lines$folder == folder, ], aes(x=line)) +
        geom_point(aes(y=p_hat), size=1) +
        theme_classic() +
        theme(legend.position=c(0.75, 1), legend.justification=c(0, 1)) +
        ylab("Predicted probability") +
        xlab('Paragraph number') +
        geom_ribbon(data=regions[regions$folder == folder, ], aes(x=x, ymax=ymax, ymin=ymin, group=Region, fill=Region), alpha=0.25) +
        ggtitle(folder)
        )
    print(g)
}

print_detailed_graphs <- function() {
    for (i in unique(lines$folder)) {
        print_graph(i)
        cat('\n\n\\clearpage\n\n')
    }
}

compare_regions <- function() {
    a <- actual_regions %>% select(folder, actual=x) %>% arrange(folder, actual)
    a$start <- 1:nrow(a) %% 2

    b <- predicted_regions %>% select(folder, predicted=x) %>% arrange(folder, predicted)
    b$start <- 1:nrow(b) %% 2

    merged <- inner_join(a, b, by=c('folder', 'start'))

    g <- (
        ggplot(merged, aes(x=actual, y=predicted, group=folder)) +
        geom_point(alpha=0.5) +
        geom_line(alpha=0.5) +
        theme_classic() +
        geom_abline(intercept=0, slope=1, color='blue', alpha=0.25) +
        xlab('Actual') + ylab('Predicted') + ggtitle('Comparison of bio regions') +
        coord_fixed()
        )
    print(g)
}
