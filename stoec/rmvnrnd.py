# ///-----------------------------------------------------------------
# ///   Description:    <STOEC>
# ///   Author:         <Hadi Salman>                    
# ///   Date:           <Oct 13th 2017>
# ///   Revision History: ---
# ///-----------------------------------------------------------------

import numpy as np
from numpy import matlib
import math
from IPython import embed
from TruncatedGaussian import TruncatedGaussian

def rmvnrnd(mu,sigma,N,A,b,rhoThr,debug):

	defaulRhoThr=2.9e-4

	rhoThr=defaulRhoThr

	if 'A' in locals():
		A=A.T
	else:
		A=[]	
	if 'b' in locals():	
		b=b.T
	else:
		b=[]

	if 'mu' in locals():
		p=len(mu)

		if len(mu)==1:
			mu=mu.T
	else:
		print("error:mean vector mu must be supplied")
	
	m=A.shape[1]
	if m==0:
		A=np.zeros((p,1))
		B=np.zeros((1,1))
	X=np.zeros((N,p))
	nar=0
	ngibbs=0
	rho=1.0

	if rhoThr<1:

		n=0
		maxSample=1e6
		trials=0
		passes=0
		s=N
		while n<N and (rho>rhoThr or s<maxSample):
			R=np.random.multivariate_normal(mu,sigma,s)
			temp = np.array((np.matrix(R)*np.matrix(A)<=np.matlib.repmat(b,np.matrix(R).shape[0],1)).sum(axis=1)==np.matrix(A).shape[1]).flatten()
			R=np.matrix(R)[np.nonzero(temp)[0],:]
			# print(R.shape)

			if R.shape[0]>0:
				X[(n):min(N,(n+R.shape[0])),:]=R[0:min(N-n,R.shape[0]),:]
				nar=nar + min(N,(n+R.shape[0]))-n
			n=n+R.shape[0]
			trials=trials+s
			rho=n/trials
			if rho>0:
				s=min([maxSample,math.ceil((N-n)/rho),10*s])
			else:
				s=min([maxSample,10*s])

			passes=passes+1
		
	if nar<N:
		if nar>	0:
			x=X[nar-1,:]
		else:
			x=np.array(mu)
	SigmaInv=np.linalg.inv(sigma)
	n=nar
	# embed()
	while n<N:
		for i in range(0,p):
			Sigmai_i=sigma[range(0,i-1)+ range(i+1,p),i]

			Sigmai_i_iInv = SigmaInv[range(0,i-1)+range(i+1,p),range(0,i-1)+range(i+1,p)]-SigmaInv[range(0,i-1)+range(i+1,p),i]*SigmaInv[range(0,i-1)+range(i+1,p),i].T/SigmaInv[i,i]

			x_i=x[range(0,i-1)+range(i+1,p)]

			mu_i=np.array(mu)[range(0,i-1)+range(i+1,p)]
			# embed()
			mui=mu[i]+Sigmai_i.T*Sigmai_i_iInv*(np.matrix(x_i).T- np.matrix(mu_i).T)

			s2i=sigma[i,i]-Sigmai_i.T*Sigmai_i_iInv*Sigmai_i

			A_i=A[range(0,i-1)+range(i+1,p),:]

			Ai=A[i,:]
			# embed()
			
			c=np.divide((b- np.matrix(x_i)*A_i),Ai)


			lb=np.max(np.array(c)[0][Ai<0])
			if not lb:
				lb=-float("inf")

			ub=	np.min(np.array(c)[0][Ai>0])
			if not ub:
				ub=float("inf")
			# embed()
			x[i]=mui[0,0]+TruncatedGaussian(-np.sqrt(s2i)[0,0],[lb,ub]-mui[0,0],1)	
		n=n+1
		# embed()
		X[n-1,:]=x
		ngibbs=ngibbs+1

	return X
