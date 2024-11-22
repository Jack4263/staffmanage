args = ["companyName","branchName"]
noArgs = len(args)

FullQuery = f"""
          SELECT Username
          FROM {','.join(['Company','Branch',''][:noArgs])}
          WHERE Company.CompanyName = '{args[0]}'
          """
query2 = f"""
          AND Company.CompanyID = Branch.BranchID
          AND Branch.BranchName = '{args[1]}'
          """

FullQuery +=  query2
print(FullQuery)