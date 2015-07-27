library(survival)
library(testthat)
library(stringr)
library(dplyr)

assert <- stopifnot

Corpus <- function(depvar, indepvars, strata) {
    strata_term <- paste0('strata(', strata, ')')
    rhs <- paste(c(indepvars, strata_term), collapse=' + ')
    f <- paste(depvar, '~', rhs)
    obj <- list(depvar=depvar, indepvars=indepvars, strata=strata, formula=f)
    class(obj) <- append(class(obj), 'Corpus')
    return(obj)
}

fit.Corpus <- function(self, data) {
    self$fit <- clogit(as.formula(self$formula), data)
    return(self)
}

predict.Corpus <- function(self, data) {
    beta <- as.vector(coefficients(self$fit))
    formula.string <- paste(c('~ 0', self$indepvars), collapse=' + ')
    X <- model.matrix(as.formula(formula.string), data)
    df <- data.frame(
        strata=data[[self$strata]],
        xb=X %*% beta
        )
    .phat <- function(x) exp(x) / sum(exp(x))
    data2 <- df %>% group_by(strata) %>% mutate(phat=.phat(xb))
    return(data2$phat)
}

mean_log_loss.Corpus <- function(self, data) {
    p <- predict.Corpus(self, data)
    y <- data[, self$depvar]
    assert(y == 0 | y == 1)
    eqn <- paste0('sum(', self$depvar, ')')
    totals <- data %>% group_by_(self$strata) %>% summarise_(y=eqn)
    assert(all(totals$y == 1))
    -mean(log(p[y == 1]))
}

cross_validate.Corpus <- function(self, data, k=10) {
    ids <- unique(data[[self$strata]])
    group <- sample((1:length(ids)) %% k)
    df <- data.frame(group=group)
    df[[self$strata]] <- ids
    data <- left_join(data, df, by=self$strata)

    log_losses <- sapply(unique(group), function(i) {
        test <- data[data$group == i, ]
        train <- data[data$group != i, ]
        corpus <- fit.Corpus(self, train)
        log_loss <- mean_log_loss.Corpus(corpus, test)
    })
    return(mean(log_losses))
}

## Tests

example_data <- function() {
    df <- read.csv('temp.csv')
    df <- df %>% group_by(idcode) %>% arrange(year) %>% mutate(union_years=cumsum(union))
    df$join <- df$union == 1 & df$union_years == 1
    df <- df %>% group_by(idcode) %>% filter(max(join) == 1)
    return(df)
}

test_that("Corpus methods work", {
    corpus <- Corpus(depvar='join', indepvars=c('age', 'grade', 'not_smsa'), strata='idcode')
    expect_equal(length(corpus), 4)
    expect_equal(corpus$formula, 'join ~ age + grade + not_smsa + strata(idcode)')

    data <- example_data()
    corpus <- fit.Corpus(corpus, data)
    expect_equal(length(corpus), 5)

    newdata <- data[data$id %in% c(1, 2), ]
    p <- predict.Corpus(corpus, newdata)
    expect_equal(length(p), nrow(newdata))

    mean_log_loss <- mean_log_loss.Corpus(corpus, newdata)
    expect_true(mean_log_loss >= 0)

    multi_class_log_loss <- cross_validate.Corpus(corpus, data)
    expect_true(multi_class_log_loss >= 0)
})
