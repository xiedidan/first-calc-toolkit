# Requirements Document

## Introduction

本文档定义了科室运营分析报告功能的需求。该功能旨在为医疗机构提供科室级别的业务价值分析报告，帮助管理层和科室负责人了解科室的业务分布、业务内涵，并支持对科室当前问题和未来发展计划的记录与管理。

## Glossary

- **System**: 科室运营分析报告系统
- **Report**: 科室运营分析报告，包含科室主业价值分布、业务内涵、当前问题和未来计划
- **Department User**: 科室用户，只能查看所属科室的报告
- **Admin User**: 管理员用户，可以管理所有科室的报告
- **Value Distribution**: 科室主业价值分布，展示业务价值金额Top10的维度
- **Business Content**: 科室业务内涵，展示业务价值Top10维度对应的Top20业务项目
- **Markdown Editor**: 可视化Markdown编辑器，用于编辑文本内容

## Requirements

### Requirement 1

**User Story:** 作为系统管理员，我希望能够访问运营分析报告菜单，以便查看和管理科室分析报告。

#### Acceptance Criteria

1. WHEN the System displays the main menu THEN the System SHALL include an "运营分析报告" menu item
2. WHEN a user clicks the "运营分析报告" menu item THEN the System SHALL expand to show two sub-menu items: "分析报告查看" and "分析报告管理"
3. WHEN a user clicks "分析报告查看" THEN the System SHALL navigate to the report viewing page
4. WHEN a user clicks "分析报告管理" THEN the System SHALL navigate to the report management page

### Requirement 2

**User Story:** 作为用户，我希望能够查看科室分析报告列表，以便了解各科室的报告情况。

#### Acceptance Criteria

1. WHEN a user accesses the report viewing page THEN the System SHALL display a list of all accessible reports with columns: ID, 年月, 科室代码, 科室名称, and 操作
2. WHEN a user sorts by 年月 column THEN the System SHALL reorder the list by period in ascending or descending order
3. WHEN a user filters by 年月 THEN the System SHALL display only reports matching the selected period
4. WHEN a user sorts by 科室代码 column THEN the System SHALL reorder the list by department code in ascending or descending order
5. WHEN a user searches by 科室代码 THEN the System SHALL display only reports where department code contains the search term
6. WHEN a user sorts by 科室名称 column THEN the System SHALL reorder the list by department name in ascending or descending order
7. WHEN a user searches by 科室名称 THEN the System SHALL display only reports where department name contains the search term

### Requirement 3

**User Story:** 作为科室用户，我希望只能看到自己所属科室的报告，以便保护其他科室的数据隐私。

#### Acceptance Criteria

1. WHEN a department user accesses the report viewing page THEN the System SHALL filter reports to show only those belonging to the user's department
2. WHEN a department user attempts to view a report from another department THEN the System SHALL deny access and display an error message
3. WHEN an admin user accesses the report viewing page THEN the System SHALL display reports from all departments

### Requirement 4

**User Story:** 作为用户，我希望能够查看报告详情，以便了解科室的业务价值分布和业务内涵。

#### Acceptance Criteria

1. WHEN a user clicks the "查看详情" button for a report THEN the System SHALL open a modal dialog displaying the report details
2. WHEN the report details modal opens THEN the System SHALL display four sections: 科室主业价值分布, 科室业务内涵展示, 当前存在问题, and 未来发展计划
3. WHEN displaying 科室主业价值分布 THEN the System SHALL show a list of the top 10 dimensions by business value amount from the calculation results
4. WHEN displaying 科室业务内涵展示 THEN the System SHALL show a list of the top 20 business items corresponding to the top 10 dimensions by business value
5. WHEN displaying 当前存在问题 THEN the System SHALL render the text content as Markdown format
6. WHEN displaying 未来发展计划 THEN the System SHALL render the text content as Markdown format

### Requirement 5

**User Story:** 作为管理员，我希望能够管理科室分析报告，以便创建、编辑和删除报告。

#### Acceptance Criteria

1. WHEN an admin user accesses the report management page THEN the System SHALL display a list of all reports with columns: ID, 年月, 科室代码, 科室名称, and 操作
2. WHEN the report management page displays the 操作 column THEN the System SHALL include "编辑详情" and "删除" buttons for each report
3. WHEN an admin user clicks the "编辑详情" button THEN the System SHALL open an editable modal dialog with the report details
4. WHEN an admin user clicks the "删除" button THEN the System SHALL prompt for confirmation before deleting the report
5. WHEN an admin user confirms deletion THEN the System SHALL remove the report from the database and refresh the list

### Requirement 6

**User Story:** 作为管理员，我希望能够编辑报告的问题分析和发展计划，以便记录科室的管理信息。

#### Acceptance Criteria

1. WHEN the edit modal opens THEN the System SHALL display the 科室主业价值分布 section as read-only with system-generated data
2. WHEN the edit modal opens THEN the System SHALL display the 科室业务内涵展示 section as read-only with system-generated data
3. WHEN the edit modal opens THEN the System SHALL display the 当前存在问题 section with a visual Markdown editor
4. WHEN the edit modal opens THEN the System SHALL display the 未来发展计划 section with a visual Markdown editor
5. WHEN a user types in the Markdown editor for 当前存在问题 THEN the System SHALL limit the input to 2000 characters maximum
6. WHEN a user types in the Markdown editor for 未来发展计划 THEN the System SHALL limit the input to 2000 characters maximum
7. WHEN a user saves the edited report THEN the System SHALL validate the Markdown content and update the database

### Requirement 7

**User Story:** 作为管理员，我希望系统能够自动生成科室主业价值分布和业务内涵数据，以便减少手工录入工作。

#### Acceptance Criteria

1. WHEN creating or updating a report THEN the System SHALL automatically extract the top 10 dimensions by business value from the calculation_results table for the specified department and period
2. WHEN creating or updating a report THEN the System SHALL automatically extract the top 20 business items corresponding to the top 10 dimensions from the charge_details table
3. WHEN the calculation results are not available for the specified department and period THEN the System SHALL display a warning message indicating no data is available
4. WHEN displaying dimension data THEN the System SHALL include dimension name and business value amount
5. WHEN displaying business item data THEN the System SHALL include item name, item code, and associated value

### Requirement 8

**User Story:** 作为用户，我希望报告数据能够按医疗机构隔离，以便支持多租户环境。

#### Acceptance Criteria

1. WHEN any user accesses report data THEN the System SHALL filter all queries by the current hospital_id
2. WHEN creating a new report THEN the System SHALL automatically set the hospital_id to the current user's hospital
3. WHEN a user from one hospital attempts to access a report from another hospital THEN the System SHALL deny access and return a 403 error
4. WHEN joining with related tables THEN the System SHALL apply hospital_id filtering to all joined tables

### Requirement 9

**User Story:** 作为用户，我希望报告列表支持分页，以便在大量报告时提高性能。

#### Acceptance Criteria

1. WHEN the report list page loads THEN the System SHALL display a maximum of 20 reports per page by default
2. WHEN a user navigates to a different page THEN the System SHALL load and display the reports for that page
3. WHEN a user changes the page size THEN the System SHALL reset to page 1 and display the specified number of reports per page
4. WHEN applying filters or search THEN the System SHALL reset to page 1 and apply the filters to the entire dataset
