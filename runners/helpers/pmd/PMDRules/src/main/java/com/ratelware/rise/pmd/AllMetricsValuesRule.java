package com.ratelware.rise.pmd;

import net.sourceforge.pmd.lang.java.ast.*;
import net.sourceforge.pmd.lang.java.metrics.api.JavaClassMetricKey;
import net.sourceforge.pmd.lang.java.metrics.api.JavaOperationMetricKey;
import net.sourceforge.pmd.lang.java.rule.AbstractJavaRule;
import net.sourceforge.pmd.lang.metrics.MetricsUtil;

import java.util.Arrays;

public class AllMetricsValuesRule extends AbstractJavaRule {
    @Override
    public String getRuleSetName() {
        return "java-metrics";
    }

    public Object visit(ASTClassOrInterfaceDeclaration node, Object data) {
        for(JavaClassMetricKey metric : JavaClassMetricKey.values()) {
            if(MetricsUtil.supportsAll(node, metric)) {
                double metricValue = MetricsUtil.computeMetric(metric, node);
                addViolationWithMessage(data, node, metric.name() + ":" + String.valueOf(metricValue));
            }
        }

        return super.visit(node, data);
    }

    public Object visit(ASTMethodDeclaration node, Object data) {
        for(JavaOperationMetricKey metric : JavaOperationMetricKey.values()) {
            if(MetricsUtil.supportsAll(node, metric)) {
                double metricValue = MetricsUtil.computeMetric(metric, node);
                addViolationWithMessage(data, node, metric.name() + ":" + String.valueOf(metricValue));
            }
        }

        return super.visit(node, data);
    }
}
